import os
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from PIL import Image, ImageFont, ImageDraw

load_dotenv()

#
# Why did I not make this earlier??
#
# Yes, I know that most of this code is awful in
# many respects and devoid of any programmatic
# brilliance, but after hours tweaking pixels it
# seems (mainly) to work, and I won't touch it to
# try to make it prettier. Hopefully it doesn't
# explode! -Ben
#


def get_slide_nums(dir):
    files = os.listdir(dir)
    max = 0
    for file in files:
        if file[:5] == "Slide":
            num = int(file.split(".")[0][6:])
            if num > max:
                max = num
    return max + 1


CCLI_NUM = os.environ["CCLI"]
dir = os.environ["DIRECTORY"]
token = os.environ["ESV_API_TOKEN"]
hymnal = os.environ["HYMNAL"]
CCLI = f"CCLI License #{CCLI_NUM}"
text_font = ImageFont.truetype("text.ttf", size=22)
bold_font = ImageFont.truetype("bold.ttf", size=72)
small_font = ImageFont.truetype("bold.ttf", size=52)


class Group:
    def __init__(self, title, verse=None, hymn=None):
        self.title = title
        self.verse = None
        self.hymn_num = None
        if verse:
            self.verse = verse
            self.blank_slide()
            text = self.get_verse_text()
            self.write_verses(text)
        if hymn:
            self.hymn_num = hymn
            self.blank_slide()
            text = self.get_hymn_text(str(hymn))
            self.write_hymn(text)

    def blank_slide(self):
        self.img = Image.new("RGB", (1920, 1080), color="white")
        logo = Image.open("logo.jpg")
        logo = logo.resize((556, 156))
        self.img.paste(logo, (1300, 850))
        self.draw = ImageDraw.Draw(self.img)
        self.draw.text((145, 73), self.title, font=bold_font, fill="black")
        if self.hymn_num:
            self.draw.text((1510, 990), CCLI, font=text_font, fill="black")

    def write_lines(self, text, x, y, step, indent):
        buffer = ""
        last = x
        for word in text.split(" "):
            max_size = 1530
            buffer += word + " "
            size = self.draw.textlength((" " * indent + buffer), bold_font)
            if y > 900:
                slide_num = get_slide_nums(dir)
                self.img.save(f"{dir}/Slide {slide_num}.png")
                self.blank_slide()
                y = 173
            if y > 800:
                max_size = 1000
            if size + last > max_size:
                self.draw.text(
                    (270 + last, y),
                    (" " * indent + buffer[: -(len(word) + 1)]),
                    font=bold_font,
                    fill="black",
                )
                y += step
                last = 0
                buffer = word + " "
        self.draw.text(
            (270 + last, y), (" " * indent + buffer[:-1]), font=bold_font, fill="black"
        )
        if (indent > 1) and (y + step > 900):
            slide_num = get_slide_nums(dir)
            self.img.save(f"{dir}/Slide {slide_num}.png")
            self.blank_slide()
            y = 86
        return (self.draw.textlength(" " * indent + buffer[:-1], bold_font), y)

    def write_verses(self, text):
        y = 173
        x = 0
        lined = False
        psalm_dedication = False
        for verse in text:
            lines = verse[1].rstrip().split("\n")
            indent = 0
            if verse[0]:
                if x > 1500:
                    y += 76
                    x = 0
                self.draw.text(
                    (270 + x, y - 7),
                    str(verse[0]),
                    font=small_font,
                    fill="dimgray",
                )
                space = self.draw.textlength(str(verse[0]), small_font) + 10
                x += space
                indent = 1 + round(space / 36)
            else:
                psalm_dedication = True
            if len(lines) > 1:
                x -= space
                lined = True
                for line in lines:
                    whitespace = True
                    tick = 1
                    while whitespace:
                        if line[:tick].isspace():
                            indent += 1
                            tick += 1
                        else:
                            whitespace = False
                    x, y = self.write_lines(line.strip(), x, y, 90, indent)
                    x = 0
                    # if y > 174:
                    y += 90
                    indent = 0
            else:
                x, y = self.write_lines(verse[1].rstrip(), x, y, 76, 0)
                if psalm_dedication:
                    y += 90
                    x = 0
                    psalm_dedication = False
        if not lined:
            slide_num = get_slide_nums(dir)
            self.img.save(f"{dir}/Slide {slide_num}.png")

    def write_hymn(self, hymn):
        text = ""
        y = 173
        lines = 1
        dir = "slides"
        if len(hymn[0]) > 4:
            for stanza in hymn:
                for line in stanza:
                    if self.draw.textlength(line, bold_font) < 1530:
                        self.draw.text((270, y), line, font=bold_font, fill="black")
                        y += 76
                slide_num = get_slide_nums(dir)
                self.img.save(f"{dir}/Slide {slide_num}.png")
                self.blank_slide()
                y = 173
        else:
            pass

    def get_verse_text(self):
        token = os.environ["ESV_API_TOKEN"]
        headers = {"Authorization": f"Token {token}"}
        verses = []
        resp = requests.get(
            f"https://api.esv.org/v3/passage/text/?q={self.verse}&include-footnote-body=false&include-footnotes=false&include-headings=false&include-passage-references=false",
            headers=headers,
        )
        text = resp.json()["passages"][0][:-6]
        for verse in text.split("["):
            if len(verse.strip()) > 1:
                try:
                    verses.append((int(verse[:2]), verse[3:]))
                except:
                    try:
                        verses.append((int(verse[:1]), verse[3:]))
                    except:
                        verses.append((None, verse.rstrip()))
        return verses

    def get_hymn_text(self, num):
        cookie = {f"license_{hymnal}_{num}_1": "yes"}
        url = f"https://hymnary.org/hymn/{hymnal}/{num}"
        link = requests.get(url, cookies=cookie)
        html = str(link.text)
        soup = BeautifulSoup(html, "html.parser")
        stanza = []
        hymn = []
        refrain = None
        ref_true = False
        for ref in soup.find_all("div", {"id": "text"}):
            verses = ref.findChildren("p")
            for verse in verses:
                for line in str(verse).split("<br/>"):
                    line = line.replace("</p>", "")
                    line = line.replace("<br/>", "")
                    if line[:3] == "<p>" and line[3:][:1].isdigit():
                        if ref_true:
                            refrain = stanza
                            ref_true = False
                        else:
                            hymn.append(stanza)
                        stanza = []
                        stanza.append(line[5:])
                    elif line[:3] == "<p>" and line[3:][:1] == "R":
                        ref_true = True
                        hymn.append(stanza)
                        stanza = []
                    elif "[Refrain]" in line:
                        stanza.append(line[2:][:-10])
                    else:
                        if len(line) > 1 and line[:7] != "<p><div":
                            stanza.append(line[2:])
            hymn.append(stanza)
            if refrain:
                for num, stave in enumerate(hymn):
                    stave.append("")
                    hymn[num] = stave + refrain
        hymn.pop(0)
        return hymn


for file in os.listdir("slides"):
    os.remove("slides/" + file)
# Group("445. Bring Them In", None, 499)
Group("Psalm 1:1-5", "Daniel 2:1-15", None)
