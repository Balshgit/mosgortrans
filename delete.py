import time

index = 0
while True:
    index += 1
    print(index, round(time.time() / 25))
    time.sleep(1)