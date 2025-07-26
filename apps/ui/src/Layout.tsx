import { Box, Flex } from "@chakra-ui/react";
import Header from "./Header";
import FileTree from "./FileTree";
import ParameterPanel from "./ParameterPanel";

const Layout = ({ children }) => {
  return (
    <Flex>
      <FileTree />
      <Box flex="1">
        <Header />
        <Flex>
          <Box flex="1" p="4">
            {children}
          </Box>
          <ParameterPanel />
        </Flex>
      </Box>
    </Flex>
  );
};

export default Layout;
