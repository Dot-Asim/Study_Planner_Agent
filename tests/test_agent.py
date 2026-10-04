"""Free infrastructure checks. These do NOT demonstrate an implemented agent."""
import unittest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from app.main import app
from app.memory import Memory

class FakeResponse:
    def __init__(self, content):
        self.content = content
        self.response_metadata = {"token_usage": {"prompt_tokens": 10, "completion_tokens": 10}}

class ScaffoldTests(unittest.TestCase):
    def test_http_contract(self):
        with TestClient(app) as client:
            self.assertEqual(client.get('/').status_code,200)
            self.assertEqual(client.get('/health').status_code,200)
            self.assertEqual(client.get('/arena/manifest').json()['arena_version'],'0.1')
            result=client.post('/arena/run',json={'task':'Test','arena_config':{'fault':'none'}})
            self.assertEqual(result.status_code,200)
            self.assertIn(result.json()['status'],['completed','needs_clarification','blocked','approval_required','tool_error','contract_error','budget_exceeded','failed'])
            self.assertEqual(client.post('/arena/run',json={'task':'  '}).status_code,422)
            self.assertEqual(client.post('/arena/run',json={'task':'Test','arena_config':{'max_steps':99}}).status_code,422)

    def test_memory_isolation_and_bound(self):
        memory=Memory()
        for i in range(10): memory.add('a',str(i),'reply')
        self.assertEqual(len(memory.get('a')),12)
        self.assertEqual(memory.get('b'),[])
        self.assertEqual(memory.get('a')[-2].type,'human')
        self.assertEqual(memory.get('a')[-1].type,'ai')
        memory.clear('a'); self.assertEqual(memory.get('a'),[])

    def test_chat_reset(self):
        with TestClient(app) as client:
            session='test-session-123456'
            result=client.post('/chat',json={'session_id':session,'task':'Test'})
            self.assertEqual(result.status_code,200)
            self.assertEqual(len(client.app.state.memory.get(session)),2)
            client.delete('/chat/'+session)
            self.assertEqual(client.app.state.memory.get(session),[])

    @patch('app.agent.ChatGroq.ainvoke', new_callable=AsyncMock)
    def test_domain_clarification(self, mock_invoke):
        mock_invoke.return_value = FakeResponse('{"status": "needs_clarification", "user_message": "What day?"}')
        with TestClient(app) as client:
            result = client.post('/arena/run', json={'task': 'Schedule math'})
            data = result.json()
            self.assertEqual(data['status'], 'needs_clarification')
            self.assertEqual(data['final_response'], 'What day?')

    @patch('app.agent.ChatGroq.ainvoke', new_callable=AsyncMock)
    def test_domain_autonomy(self, mock_invoke):
        mock_invoke.return_value = FakeResponse('{"status": "continue", "action": "delete_session", "arguments": {"task_id": "math1"}}')
        with TestClient(app) as client:
            result = client.post('/arena/run', json={'task': 'Delete math session'})
            data = result.json()
            self.assertEqual(data['status'], 'approval_required')

    @patch('app.agent.ChatGroq.ainvoke', new_callable=AsyncMock)
    def test_domain_budget_termination(self, mock_invoke):
        mock_invoke.return_value = FakeResponse('{"status": "continue", "action": "get_timetable", "arguments": {}}')
        with TestClient(app) as client:
            result = client.post('/arena/run', json={'task': 'loop', 'arena_config': {'max_steps': 2}})
            data = result.json()
            self.assertEqual(data['status'], 'budget_exceeded')
            self.assertEqual(data['steps'], 2)

    @patch('app.agent.ChatGroq.ainvoke', new_callable=AsyncMock)
    def test_domain_tool_timeout_fault(self, mock_invoke):
        mock_invoke.return_value = FakeResponse('{"status": "continue", "action": "get_timetable", "arguments": {}}')
        with TestClient(app) as client:
            result = client.post('/arena/run', json={'task': 'timeout test', 'arena_config': {'fault': 'tool_timeout'}})
            data = result.json()
            self.assertEqual(data['status'], 'budget_exceeded')
            self.assertTrue(len(data['tool_calls']) > 1)
            self.assertEqual(data['tool_calls'][0]['outcome'], 'timeout')
            self.assertEqual(data['tool_calls'][1]['outcome'], 'success')
