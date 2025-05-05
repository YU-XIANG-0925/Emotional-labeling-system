import re

class EmotionHighlighter:
    def __init__(self):
        self.emotion_map = {
            'positive': ['喜悅', '歡喜', '快樂', '期待'],
            'negative': ['驚恐', '恐懼', '憤怒', '厭惡', '悲傷'],
            'neutral':  ['冷靜', '平穩', '中性', '理智']
        }

    def get_color(self, emotion):
        if emotion in self.emotion_map['positive']:
            return '#0000FF'
        elif emotion in self.emotion_map['negative']:
            return '#FF0000'
        elif emotion in self.emotion_map['neutral']:
            return '#00FF00'
        return '#000000'

    def highlight(self, text):
        # pattern: 取得任意連續中文字或標點，後面接 [情緒]
        pattern = r'([\u4e00-\u9fffA-Za-z0-9！？。，、…“”「」《》\-—\s]{1,20})\[(.*?)\]'

        def replacer(match):
            phrase = match.group(1)
            emotion = match.group(2)
            color = self.get_color(emotion)
            return f'<font color="{color}" class="emotion-word" data-emotion="{emotion}">{phrase}</font>'


        return re.sub(pattern, replacer, text)