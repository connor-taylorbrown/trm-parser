from corpus import Conversation, TokenType


class ConversationFormatter:
    def __init__(self, format):
        self.format = format

    def format_date(self, conversation: Conversation):
        if self.format & 1:
            return conversation.date
        else:
            return conversation.parse_date()
        
    def print_text(self, text):
        t, v = text
        if t != TokenType.content:
            return text
        
        if self.format & 2:
            return (t, v)
        else:
            return (t, ' '.join(word.text for word in v))


class Summary:
    def __init__(self, formatter: ConversationFormatter, conversations: list[Conversation], all, count):
        self.formatter = formatter
        self.conversations = conversations
        self.all = all
        self.count = count

    def summarise(self, conversation: Conversation):
        summary = {}
        def total(speaker):
            count = summary.get(speaker)
            if not count:
                summary[speaker] = 0
            
            summary[speaker] += 1

        for turn in conversation.turns:
            if self.count == 'turns':
                total(turn.speaker)
                continue

            for _ in turn.text:
                total(turn.speaker)

        return summary

    def summarise_all(self):
        all = {}
        for conversation in self.conversations:
            summary = self.summarise(conversation)
            for speaker in summary:
                running = all.get(speaker)
                if not running:
                    all[speaker] = 0
                
                all[speaker] += summary[speaker]
        
        for k in all:
            yield all[k], k

    def summarise_conversations(self):
        for conversation in self.conversations:
            summary = self.summarise(conversation)

            c = 0
            for k in summary:
                c += summary[k]

            yield conversation.document, self.formatter.format_date(conversation), len(summary), c, summary

    def show(self):
        if self.all:
            lines = self.summarise_all()
        else:
            lines = self.summarise_conversations()
        
        for line in lines:
            print(*line)