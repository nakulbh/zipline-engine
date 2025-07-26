import Editor from "@monaco-editor/react";

const StrategyEditor = () => {
  return (
    <Editor
      height="90vh"
      defaultLanguage="python"
      defaultValue="# Enter your Python strategy here"
    />
  );
};

export default StrategyEditor;
