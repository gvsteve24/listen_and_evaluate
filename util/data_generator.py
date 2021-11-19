import csv
import os
import timeit
import argparse
from dotenv import load_dotenv

from pathlib import Path

load_dotenv()

data_root = os.environ.get('BASE_DIR')


class Argparser:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.init_parser()

    def init_parser(self):
        parser = self.parser
        parser.add_argument("--question_path", default='/home/junghyun/Downloads/questions_developer_chegg.txt', help="question_txt_filepath")
        parser.add_argument("--answer_path", default='/home/junghyun/Downloads/answers_developer_chegg.txt', help="answer_txt_filepath")
        self.parser = parser


class Generator:
    def __init__(self, args):
        self.question = Path(args.question_path).stem+'_out.csv'
        self.question_path = args.question_path
        self.answer = Path(args.answer_path).stem+'_out.csv'
        self.answer_path = args.answer_path
        self.question_pool = []
        self.answer_pool = []
        self.word_pool = self.answer_pool[0].split() if self.answer_pool else []

    def to_csv(self, type: str = "question"):
        csv_filename = self.question if type == "question" else self.answer
        txt_path = self.question_path if type == "question" else self.answer_path
        pool = self.question_pool if type == "question" else self.answer_pool
        with open(txt_path, 'r') as fq:
            contents = fq.read()
            pool.extend(contents.split('\n'))
        f = open(f"{data_root}/{csv_filename}", 'w', encoding='utf-8', newline='')
        wr = csv.writer(f)
        for i, text in enumerate(pool):
            if type == "question":
                wr.writerow([i+1]+[text])
            else:
                wr.writerow([i+1]+[True]+[text])
        f.close()



if __name__ == "__main__":
    parser = Argparser()
    args = parser.parser.parse_args()
    print("Generating file...")
    start = timeit.default_timer()
    generator = Generator(args)
    generator.to_csv(type="question")
    generator.to_csv(type="answer")
    stop = timeit.default_timer()
    print(generator.question + ' and ' + generator.answer + " is created. ")
    print("It took " + str(stop - start) + " seconds to generate data.")
