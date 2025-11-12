import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import Dashboard from './pages/Dashboard';
import NovelEditor from './pages/NovelEditor';
import { AIAssistantProvider } from './contexts/AIAssistantContext';

function App() {
  return (
    <ConfigProvider locale={zhCN}>
      <AIAssistantProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/projects/:id" element={<NovelEditor />} />
            {/* 保持兼容旧路由 */}
            <Route path="/projects/:id/outline" element={<Navigate to="/projects/:id" replace />} />
            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
        </BrowserRouter>
      </AIAssistantProvider>
    </ConfigProvider>
  );
}

export default App;
