import distance_read
import asyncio
from send_message import send_notification

# Constants
DISTANCE_THRESHOLD = 5  # cm
CHECK_INTERVAL = 1  # second

# Main program
async def main():
    try:
        previous_dist = None
        door_state = "closed"  # Initial state

        print("Door Monitor Started. Press CTRL+C to exit.")

        while True:
            dist = distance_read.get_distance()
            print("Measured Distance = {:.2f} cm".format(dist))

            if previous_dist is not None:
                distance_change = abs(dist - previous_dist)

                if distance_change > DISTANCE_THRESHOLD:
                    if door_state == "closed":
                        door_state = "open"
                        await send_notification(f"🚪 Door opened! Distance changed by {distance_change:.2f} cm")
                    else:
                        door_state = "closed"
                        await send_notification(f"🚪 Door closed! Distance changed by {distance_change:.2f} cm")

            previous_dist = dist
            await asyncio.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        print("\nDoor Monitor stopped by user.")
    except Exception as error:
        print(f"An error occurred: {error}")
        await send_notification(f"⚠️ Error in Door Monitor: {error}")

if __name__ == '__main__':
    asyncio.run(main())