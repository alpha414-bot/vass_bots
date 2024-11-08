from utils.settings import Settings


class Vass:
    def __init__(self):
        self.start()

    def start(self):
        print("hello")

        if Settings.USE_PROXY:
            print("plan on using proxy")


if __name__ == "__main__":
    Vass()
