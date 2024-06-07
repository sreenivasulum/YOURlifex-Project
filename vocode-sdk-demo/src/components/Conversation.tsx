import { 
  Box, Button, HStack, VStack, Select, Spinner, Text,
  Stack, 
  Image,
  Container,
  Card,
  CardBody} from "@chakra-ui/react";
import React from "react";
import queryString from 'query-string';
import { useConversation, AudioDeviceConfig, ConversationConfig } from "vocode";
import MicrophoneIcon from "./MicrophoneIcon";
import AudioVisualization from "./AudioVisualization";
import { isMobile } from "react-device-detect";

const Conversation = ({
  config,
}: {
  config: Omit<ConversationConfig, "audioDeviceConfig">;
}) => {
  const [audioDeviceConfig, setAudioDeviceConfig] =
    React.useState<AudioDeviceConfig>({});
  const [inputDevices, setInputDevices] = React.useState<MediaDeviceInfo[]>([]);
  const [outputDevices, setOutputDevices] = React.useState<MediaDeviceInfo[]>(
    []
  );
  let transcripts: any[] = [];
  const params = queryString.parse(window.location.search);
  const user_id : string = String(params.user_id);
  const [HumanUserID] = React.useState(user_id);
  const [BotUserID] = React.useState(user_id);

  let { status, start, stop, analyserNode } = useConversation({
    backendUrl: `wss://lifex-backend-api-users-v1-aoomkpbnqq-nw.a.run.app/conversation/${BotUserID}/${HumanUserID}`,
    audioDeviceConfig: {},
  });
  
  const [apiData, setApiData] = React.useState<any>(null); // Store API data
  const [isLoading, setIsLoading] = React.useState(true);
  const [showCard, setShowCard] = React.useState(false); // State to control card visibility

  React.useEffect(() => {
    const intervalId = setInterval(async () => {
      try {
        if (!showCard) {
          const response = await fetch(`https://lifex-backend-api-v1-aoomkpbnqq-nw.a.run.app/api/v1/pull_media_messages/?user_id=${BotUserID}`); // Replace with actual API URL
          if (response.ok) {
            const data = await response.json();
            setApiData(data);
            setIsLoading(false); // Set loading to false when data arrives
            setShowCard(true); // Show card after successful fetch
          } else {
            console.error('Error fetching API data:', response.status);
            setIsLoading(false);
          }
        }
      } catch (error) {
        console.error('Error fetching API data:', error);
        setIsLoading(false);
      }
    }, 5 * 1000); // Check every x seconds

    return () => clearInterval(intervalId); // Clear interval on unmount
  }, []);

  React.useEffect(() => {
    // Timer to hide the card after x seconds if it's shown
    let timeoutId: NodeJS.Timeout | null = null;
    if (showCard) {
      timeoutId = setTimeout(() => {
        setShowCard(false);
      }, 10 * 1000);
    }

    return () => {
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
    };
  }, [showCard]); // This effect depends on showCard


  React.useEffect(() => {
    navigator.mediaDevices
      .enumerateDevices()
      .then((devices) => {
        setInputDevices(
          devices.filter(
            (device) => device.deviceId && device.kind === "audioinput"
          )
        );
        setOutputDevices(
          devices.filter(
            (device) => device.deviceId && device.kind === "audiooutput"
          )
        );
      })
      .catch((err) => {
        console.error(err);
      });
  });

  return (
    <>
      {analyserNode && <AudioVisualization analyser={analyserNode} />}
      <Button
        variant="link"
        disabled={["connecting", "error"].includes(status)}
        onClick={status === "connected" ? stop : start}
        position={"absolute"}
        top={"45%"}
        left={"50%"}
        transform={"translate(-50%, -50%)"}
      >
        <Box boxSize={75}>
          <MicrophoneIcon color={"#cac5a5"} muted={status !== "connected"} />
        </Box>
      </Button>
      <Box boxSize={50} />
      {status === "connecting" && (
        <Box
          position={"absolute"}
          top="57.5%"
          left="50%"
          transform={"translate(-50%, -50%)"}
          padding={5}
        >
          <Spinner color="#FFFFFF" />
        </Box>
      )}
      
      <Container position="absolute" top={"15%"} right={"0%"} left={"70%"}>
        <VStack align="fit">
        <br/>
        {/* <Card maxWidth={"sm"} align='left' display="flex" overflowWrap="break-word" style={{  top : "0%", left: "0%", right: "25%" }}> */}
        {/* <Card maxW='sm'style={{ right: "5%" }} >
          <CardBody>
            <Image
              src='https://images.unsplash.com/photo-1555041469-a586c61ea9bc?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1770&q=80'
              alt='Green double couch with wooden legs'
              borderRadius='lg'
            />
            <Stack mt='6' spacing='3'>
              <Heading size='md'>Living room Sofa</Heading>
              <Text>
                This sofa is perfect for modern tropical spaces, baroque inspired
                spaces, earthy toned spaces and for people who love a chic design with a
                sprinkle of vintage design.
              </Text>
            </Stack>
          </CardBody>
        </Card> */}
        <br />
          {isLoading ? (
            <Text style={{ display: "none" }}>Loading...</Text> // Display loading while data fetches
          ) : showCard && status === "connected" && apiData && typeof apiData === 'object' && apiData[0] ? (
            <Card maxW='sm' style={{ right: "5%" }}>
              <CardBody>
              <Image
                    src={typeof apiData === 'object' && apiData[0] && apiData[0].signed_url ? (apiData[0].signed_url) : null}
                    alt='Green double couch with wooden legs'
                    borderRadius='lg'
              />
              <Stack mt='6' spacing='3'>
              {/* Render API data in the card */}
              {/* <Heading size='md'>Image Text</Heading> */}
              <Text>
                {apiData && typeof apiData === 'object' && apiData[0] && apiData[0].answer ? apiData[0].answer : ""}
              </Text>
              </Stack>
              </CardBody>
            </Card>
          ) : (
            <></> // Display if no data
          )}
        </VStack>
      </Container>

      {!isMobile && (
        <HStack width="25%" position="absolute" top={"10%"} left="2%">
          {inputDevices.length > 0 && (
            <Select
              color={"black"}
              borderColor={"black"}
              disabled={["connecting", "connected"].includes(status)}
              onChange={(event) =>
                setAudioDeviceConfig({
                  ...audioDeviceConfig,
                  inputDeviceId: event.target.value,
                })
              }
              value={audioDeviceConfig.inputDeviceId}
            >
              {inputDevices.map((device, i) => {
                return (
                  <option key={i} value={device.deviceId}>
                    {device.label}
                  </option>
                );
              })}
            </Select>
          )}
        </HStack>
      )}
      { transcripts.length > 0 && (
        <VStack width="35%" position="absolute" top={"50%"} height={"45%"} left="2%" alignItems="left" overflowY="auto">
          {
            transcripts.map((item, index) => {
              return <Box key={"t" + index.toString()} color="white">{item.sender}: {item.text}</Box>
            })
          }
        </VStack>
      )}
    </>
  );
};

function setValue(value: any) {
  throw new Error("Function not implemented.");
}

export default Conversation;
