from datetime import datetime


class Scene:
    def __init__(self, threshold=None):
        self.threshold = threshold
        self.now = datetime.utcnow()
        self.f = open(f"logs/{self.now.strftime('%Y-%m-%d-%H-%M-%S')}-interaction.csv", "w")
        self.f.write("timestamp;type;value\n")

    def __del__(self):
        self.f.close()

    def log(self, type_, value, timestamp=None):
        if timestamp is None:
            timestamp = datetime.utcnow()
        self.f.write(f"{timestamp};{type_};{value}\n")
        self.f.flush()


    def draw(self, screen, emg):
        pass

    def process_event(self, event):
        pass
