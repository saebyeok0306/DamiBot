from typing import List

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

from db.model.Music import Music
from db.model.Record import Record

import utils


font_prop = fm.FontProperties(fname='utils/NanumGothic.ttf', size=12)
plt.rcParams['font.family'] = font_prop.get_name()
plt.figure(figsize=(4.5, 3))
plt.tick_params(axis='x', direction='in', labelcolor='#e2e4e6')
plt.tick_params(axis='y', direction='in', labelcolor='#e2e4e6')


class ScorePlot:
    label_font = {
        'color': '#8d76bc',
        'size': 8
    }

    def __init__(self, music: Music, score_list: List[Record], other_score_list: List[Record]=None):
        self.music = music
        self.score_list = score_list
        self.other_score_list = other_score_list  # 다른 유저와 비교하고자 할 때

    def single_user_plot(self):
        standard = self.score_list[0]
        x = range(1, len(self.score_list)+1)
        y = [float(score.judge) for score in self.score_list]

        lv = [lv for lv, idx in utils.get_music_level().items() if idx == standard.level][0]

        plt.xticks(x)
        plt.plot(x, y,
                 label=f'{self.music.music_name} {standard.button}B {lv}',
                 marker='o', linestyle='--', color='#8d76bc')
        plt.xlabel('회차', fontdict=ScorePlot.label_font, loc='right')
        plt.ylabel('판정(%)', fontdict=ScorePlot.label_font, loc='top')
        plt.legend(frameon=False, labelcolor="#e2e4e6")
        plt.tight_layout()
        plt.savefig(f'temp/{standard.user_id}.png', transparent=True)
        plt.cla()
        return f'temp/{standard.user_id}.png'

    def multi_user_plot(self):
        standard = self.score_list[0]
        x = range(1, len(self.score_list) + 1)
        y = [float(score.judge) for score in self.score_list]
        other_y = [float(score.judge) for score in self.other_score_list]

        lv = [lv for lv, idx in utils.get_music_level().items() if idx == standard.level][0]

        plt.xticks(x)
        plt.plot(x, y,
                 label=f'{self.music.music_name} {standard.button}B {lv}',
                 marker='o', linestyle='--', color='#8d76bc')
        plt.plot(x, other_y,
                 label=f'{self.music.music_name} {standard.button}B {lv}',
                 marker='o', linestyle='--', color='#53456f')
        plt.legend(frameon=False, labelcolor="#e2e4e6")
        plt.tight_layout()
        plt.savefig(f'temp/{standard.user_id}.png', transparent=True)
        return f'temp/{standard.user_id}.png'

    def create_graph(self):
        if self.other_score_list:
            return self.multi_user_plot()
        return self.single_user_plot()