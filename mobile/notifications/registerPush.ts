import * as Notifications from "expo-notifications";
import { Platform } from "react-native";
import Constants from "expo-constants";
import { api } from "../lib/api";

export async function registerForPushNotificationsAsync(tokenJwt: string) {
  let finalStatus;

  const { status: existingStatus } =
    await Notifications.getPermissionsAsync();
  finalStatus = existingStatus;
  if (existingStatus !== "granted") {
    const { status } = await Notifications.requestPermissionsAsync();
    finalStatus = status;
  }
  if (finalStatus !== "granted") {
    console.log("Push notifications permission not granted");
    return;
  }

  const expoPushToken = await Notifications.getExpoPushTokenAsync({
    projectId: (Constants.expoConfig?.extra as any)?.eas?.projectId
  });

  const platform = Platform.OS;

  try {
    await api.post("/devices/register", {
      token: tokenJwt,
      platform,
      push_token: expoPushToken.data
    });
  } catch (err) {
    console.log("Failed to register device:", err);
  }
}
