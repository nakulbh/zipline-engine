import Layout from "./Layout";
import StrategyEditor from "./StrategyEditor";
import ResultsDashboard from "./ResultsDashboard";
import LogViewer from "./LogViewer";

function App() {
  return (
    <Layout>
      <StrategyEditor />
      <ResultsDashboard />
      <LogViewer />
    </Layout>
  );
}

export default App;
