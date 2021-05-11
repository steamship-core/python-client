class NludbChatbotBase:
  def __init__(self, api_key: str, server_name: str, min_confidence: float = 0.4):
    self.nludb = NLUDB(api_key)
    self.server_name = server_name
    self.min_confidence = min_confidence
    self.index = self.nludb.create_index(
        server_name, 
        MODELS.QA, 
        upsert=True
    )

  def get_fact(self, message: str) -> str:
    words = re.sub("\s\s+" , " ", message).split(' ')
    if len(words) == 0:
      return None
    first = words[0].lower()
    if first in ['fact', 'fact:', 'learn', 'learn:']:
      return " ".join(words[1:])
    return None
    
  def dispatch(self, message: str, username: str = None, roomname: str = None) -> str:
    """
    Todo: add a "forget" feature
    """
    maybe_fact = self.get_fact(message)
    if maybe_fact is not None:
      return self.add_fact(maybe_fact, username, roomname)
    return self.answer_question(message, username, roomname)

  def add_fact(self, fact: str, username: str = None, roomname: str = None) -> str:
    self.index.insert(fact)
    self.index.embed()
    return None

  def answer_question(self, question: str, username: str = None, roomname: str = None) -> Tuple[float, str]:
    resp = self.index.search(question)
    if 'hits' not in resp or len(resp['hits']) == 0:
      return None
    
    confidence = resp['hits'][0]['score']
    text = resp['hits'][0]['text']

    if confidence < self.min_confidence:
      return None
    return (confidence, text) 

class NludbChatbot(NludbChatbotBase):
  """
  This class is intended to wrap the core functionality with
  any extra personality, error messages, etc.

  Also can provide a threshold here below which either no fact is
  returned or the bot humorously tries to hedge its answer..
  """
  def __init__(self, api_key: str, server_name: str):
    super().__init__(api_key, server_name)
  
  def dispatch(self, message: str, username: str = None, roomname: str = None) -> str:
    message = message.strip()
    words = re.split('\s+', message)
    if len(message) == 0 or len(words) == 0:
      return """QQ can learn to answer questions.
 
 Learn something:
 `qq fact: Bob's birthday is in January.`
 `qq fact: See Jamie about new account setups.`
 
 Ask something:
 `qq when is Bob's birthday?`
 `qq who do I see about creating a new account?"""
    elif bot.arguments == 'forget everything you know':
      return "I don't yet know how to forget"

    maybe_fact = self.get_fact(message)
    if maybe_fact is not None:
      if len(maybe_fact.strip()) == 0:
        return "Say `qq fact Some fact: goes here` to learn something"  
      super().dispatch(message, username, roomname)
      return "{}... got it!".format(maybe_fact)
    
    # It's a question
    resp = super().dispatch(message, username, roomname)
    if resp is None:
      return "I'm not really sure how to answer that..\n\nAdd new facts with `qq fact: Some fact goes here`."
    
    score, text = resp
    return text

secret = bot.secrets.read("nludbapikey")
if secret is None:
  bot.reply("Please set the `nludbapikey` secret in https://Ab.Bot")
else:
  # if docs is None:
  # bot.reply("I haven't learned anything yet! Say `qq fact Some fact goes here` to teach me")
  user = bot.from_user['UserName']
  #bot.reply("{}".format(bot.conversation_reference))
  chatbot = NludbChatbot(secret, "AbbotDemo1")
  reply = chatbot.dispatch(bot.arguments.strip())
  bot.reply(reply)