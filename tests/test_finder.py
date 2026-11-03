import ast
import asyncio
from pathlib import Path
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock, mock_open, patch
import urllib.parse


class FinderTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        path = Path(__file__).resolve().parents[1] / 'main.py'
        nodes = [n for n in ast.parse(path.read_text()).body if isinstance(n, ast.AsyncFunctionDef) and n.name in ['finder', 'start']]
        for node in nodes:
            node.decorator_list = []
            for arg in node.args.args:
                arg.annotation = None
        self.request_error = type('RequestError', (Exception,), {})
        self.requests = SimpleNamespace(get=Mock(return_value=SimpleNamespace(status_code=200)), RequestException=self.request_error)
        self.ns = {'requests': self.requests, 'finded': [], 'asyncio': asyncio, 'urllib': urllib, 'Path': Path, '__file__': str(path)}
        exec(compile(ast.Module(body=nodes, type_ignores=[]), 'main.py', 'exec'), self.ns)
        self.file = patch('builtins.open', mock_open(read_data='example https://example.test/users/\n'))
        self.file.start()
        self.addCleanup(self.file.stop)

    async def test_results_do_not_leak_between_users(self):
        first = SimpleNamespace(text='first-user', reply=AsyncMock())
        second = SimpleNamespace(text='second-user', reply=AsyncMock())
        await self.ns['start'](first)
        await self.ns['start'](second)
        self.assertNotIn('first-user', second.reply.call_args.args[0])
        self.assertIn('second-user', second.reply.call_args.args[0])

    async def test_request_has_finite_timeout(self):
        await self.ns['finder']('nickname')
        self.assertEqual(self.requests.get.call_args.kwargs['timeout'], 10)

    async def test_requests_do_not_block_event_loop(self):
        loop = asyncio.get_running_loop()
        progressed = threading.Event()
        result = []
        def get(*args, **kwargs):
            loop.call_soon_threadsafe(progressed.set)
            result.append(progressed.wait(timeout=2))
            return SimpleNamespace(status_code=200)
        self.requests.get.side_effect = get
        await self.ns['finder']('nickname')
        self.assertEqual(result, [True])

    async def test_transport_error_does_not_expose_exception_details(self):
        self.requests.get.side_effect = self.request_error('synthetic-private-error')
        result = await self.ns['finder']('nickname')
        self.assertEqual(result, ['ошибка поиска по nickname'])

    async def test_nickname_cannot_add_query_or_fragment(self):
        await self.ns['finder']('name?query#fragment')
        self.assertEqual(self.requests.get.call_args.args[0], 'https://example.test/users/name%3Fquery%23fragment')
