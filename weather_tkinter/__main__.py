import weather
from weather import console_io
from weather_geolocationdb import get_city_by_ip
import tkinter

def show_temperature(measurement, diff):
    message = console_io.format_message(measurement, diff)
    weather_message.set(message)

def local_weather():
    weather.local_weather(
        get_city_by_ip=get_city_by_ip,
        show_temperature=show_temperature
    )

root = tkinter.Tk()
button = tkinter.Button(root, text="What's the weather like?", command=local_weather)
button.pack()
weather_message = tkinter.StringVar()
weather_message.set("The answer will be here")
message = tkinter.Label(root, textvariable=weather_message)
message.pack()

root.mainloop()