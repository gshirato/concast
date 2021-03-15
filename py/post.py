import sys
import json
from logging import getLogger, FileHandler, Formatter, DEBUG

import pyperclip

def create_header_html(comments=None):
    result = '<div class="content-head">\n'
    
    if comments is not None:
        result += f'<p class="comments">{comments}</p>'
        
    result += '</div>'
    return result
    
def create_references_html(references_dict):
    result = '<div class="references">\n'
    result += '<ul class="list_test-wrap">\n'
    for text, link in references_dict.items():
        result += f'<li class="list_test"><a href="{link}">{text}</a></li>\n'
    result += '</ul>\n\n'
    result += '</div>'
    return result


def main():
    argv = sys.argv
    episode_number = argv[1]
    episode_name = 'episode' + episode_number

    logger = getLogger(f'postproduction-{episode_name}')
    logger.setLevel(DEBUG)

    f_handler = FileHandler(f'log/{episode_name}.log')
    f_handler.setLevel(DEBUG)

    # ログ出力フォーマット設定
    handler_format = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    f_handler.setFormatter(handler_format)
    logger.addHandler(f_handler)


    with open(f'json/{episode_name}.json', 'r') as f:
        data = json.load(f)

    number = data["Number"]
    title = data["Title"]
    topics = data['Topics']
    starr = ", ".join(data["Starr"])

    if episode_name.split('episode')[-1]!=number:
        raise ValueError('Episode number is wrong.')

    title = f'#{number} {title} ({starr})'
    comments = '、'.join(topics)

    references = data['References']
    header_html = create_header_html(comments)
    references_html = create_references_html(references)

    logger.info(title)
    logger.info(header_html)
    logger.info(references_html)

    ret = title + header_html + references_html

    #copy to clipboard
    pyperclip.copy(ret)

    print('Copied to clipboard!')

    lines = [
        title,
        '\n\n',
        comments,
        '\n\n',
        '🔎iTunes、Spotifyで配信中',
        '\n\n',
        '#spocon #concast',
        '\n\n',
        'おたよりコーナー: https://forms.gle/dXgmTe38xkBSW5sx8',
        '\n\n'
        f'https://sports-con.xyz/concast-{episode_number}/'
    ]

    with open(f'sns/episode{episode_number}.txt', mode='w') as f:
        f.writelines(lines)

if __name__ == "__main__":
    main()
