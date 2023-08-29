from SLM.appGlue.DesignPaterns.SingletonAtr import Singleton


@Singleton['MessageSystem']
class MessageSystem:
    def __init__(self):
        self.subscribers = {}

    def Subscribe(self, message, subscriber, callback):
        self.subscribers.setdefault(message, []).append((subscriber, callback))

    def Unsubscribe(self, message, subscriber):
        if message in self.subscribers:
            for subscriberi in self.subscribers[message]:
                if subscriberi[0] == subscriber:
                    self.subscribers[message].remove(subscriberi)

    def SendMessage(self, message, **kwargs):
        if message in self.subscribers:
            for subscriber in self.subscribers[message]:
                subscriber[1](**kwargs)
