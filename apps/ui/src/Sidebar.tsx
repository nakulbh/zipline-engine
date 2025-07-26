import { Box } from "@chakra-ui/react";

const Sidebar = () => {
  return (
    <Box
      as="aside"
      w="250px"
      p="4"
      borderRightWidth="1px"
      display={{ base: "none", md: "block" }}
    >
      Sidebar
    </Box>
  );
};

export default Sidebar;
