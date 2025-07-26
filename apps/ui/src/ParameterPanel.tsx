import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Input,
  Select,
} from "@chakra-ui/react";

const ParameterPanel = () => {
  return (
    <Box w="300px" p="4" borderLeftWidth="1px">
      <FormControl>
        <FormLabel>Bundle</FormLabel>
        <Select placeholder="Select bundle">
          <option>Bundle 1</option>
          <option>Bundle 2</option>
        </Select>
      </FormControl>
      <FormControl mt="4">
        <FormLabel>Stocks</FormLabel>
        <Input placeholder="Enter stock symbols" />
      </FormControl>
      <FormControl mt="4">
        <FormLabel>Start Date</FormLabel>
        <Input type="date" />
      </FormControl>
      <FormControl mt="4">
        <FormLabel>End Date</FormLabel>
        <Input type="date" />
      </FormControl>
      <FormControl mt="4">
        <FormLabel>Capital</FormLabel>
        <Input type="number" />
      </FormControl>
      <Button mt="4" colorScheme="blue">
        Run Back-test
      </Button>
    </Box>
  );
};

export default ParameterPanel;
