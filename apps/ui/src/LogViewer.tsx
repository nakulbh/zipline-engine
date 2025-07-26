import { Box, List, ListItem } from "@chakra-ui/react";
import { useEffect, useState } from "react";

const LogViewer = () => {
  const [logs, setLogs] = useState([]);
  const [socket, setSocket] = useState(null);

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws/runs/1");
    ws.onmessage = (event) => {
      setLogs((prevLogs) => [...prevLogs, event.data]);
    };
    setSocket(ws);
    return () => {
      ws.close();
    };
  }, []);

  return (
    <Box h="200px" p="4" borderWidth="1px" overflowY="scroll">
      <List spacing={2}>
        {logs.map((log, index) => (
          <ListItem key={index}>{log}</ListItem>
        ))}
      </List>
    </Box>
  );
};

export default LogViewer;
