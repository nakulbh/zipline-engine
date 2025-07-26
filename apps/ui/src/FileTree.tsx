import { Box, List, ListItem } from "@chakra-ui/react";

const files = ["strategy1.py", "strategy2.py", "strategy3.py"];

const FileTree = () => {
  return (
    <Box w="250px" p="4" borderRightWidth="1px">
      <List spacing={2}>
        {files.map((file) => (
          <ListItem key={file}>{file}</ListItem>
        ))}
      </List>
    </Box>
  );
};

export default FileTree;
