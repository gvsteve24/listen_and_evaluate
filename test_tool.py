from dataclasses import dataclass

from inference import Inferer
from db_handler import DBHandler


@dataclass
class InferScore:
    score: int
    text: str


class TestTool:
    def __init__(self, db_handler: DBHandler, infer_tool: Inferer, data_dir: str = "/home/junghyun/hdd/Fox News"):
        self.db_handler = db_handler
        self.infer_tool = infer_tool
        self.data_dir = data_dir

    def run_one_inference(self, path: str) -> [InferScore]:
        item = self.db_handler.retrieve_one_path(path)
        text_result = self.infer_tool.speech_to_text(item.path)

        # stt result check
        print(text_result)

        # TODO : retrieve relevant docs from question from database
        docs = [
            """hire everybody in welcam my name is jen and a macurcoach and indeed with over ten years of experience 
            working in carer services over the years i've worked with hundreds of job seekers to help them prepare 
            for their next interviews by showing them how to create compelling talking points that they can apply to 
            answering a variety of different questions today i'm going to share a little bit of that advice with you 
            in this video we'll discuss five common intervie questions for each will discuss what employers are 
            really looking for in an answer and break down how to craft a really strong response you'll also get 
            examples of answers along the way at the end of the video will also cover a tricky question that's very 
            common to pop up in an interview room it's a tough ine so be sure to stick around to learn how you can 
            answer it with confidence let's start with our first question why do you want to work here now 
            interpiewers often asks us question to determine whether or not you're going to be a good fit for the 
            role and the company your answer will demonstrate whether or not you did your homework if hou can speak 
            well to why you would be a good match for the team""",
            """hire somebody wecome my name is jen and consulting coach in indeed with over five years of experience3 
            working in career service over the years  I've worked with hundreds of job seekers to help them prepare 
            for their next interviews by showing them how to achieve appealing breakpoints what the variousl answers 
            and questions can combine. Today Im going to share littel bit of advice with you and really kno what is 
            the strong pointwise answer and and the along the way at the end of the video will also cover a tricky 
            question that's very common to pop up in an interview room it's tough and so make sure to stick around to 
            learn how you can answer confidently. Let's start our first example question. Why do you want to work 
            here? Now interviewrs often asks us question to determine whether or not you're going to be a good fit 
            for the role and the company your answer will demonstrate whether or not you did your assignment if you 
            can speak well to why you would be a good match for the team.""",
            """hire everybody in welcome my name is Jan and a microcoach in indeed with over ten years of experience 
            working in career services over the years i've worked with hundreds of job seekers to help them prepare 
            for their next interviews by showing them how to create compelling talking points that they can apply to 
            answering a variety of different questions today i'm going to share a little bit of that advice with you 
            in this video we'll discuss five common interview questions for each will discuss what employers are 
            really looking for in an answer and break down how to craft a really strong response you'll also get 
            examples of answers along the way at the end of the video will also cover a tricky question that's very 
            common to pop up in an interview room it's a tough so be sure to stick around to learn how you can answer 
            it with confidence let's start with our first question why do you want to work here now interviewers 
            often asks us question to determine whether or not you're going to be a good fit for the role and the 
            company your answer will demonstrate whether or not you did your homework if who can speak well to why 
            you would be a good match for the team"""]

        result = self.infer_tool.calculate_score(text_result, docs)

        return text_result, result
