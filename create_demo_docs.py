"""
create_demo_docs.py — Generate sample documents for testing
Run: python create_demo_docs.py
"""

import os

def create_demo_docs():
    os.makedirs("demo_docs", exist_ok=True)

    # Sample tech company article
    with open("demo_docs/tech_companies.txt", "w", encoding="utf-8") as f:
        f.write("""Tech Industry Overview 2024

Apple Inc. was founded by Steve Jobs, Steve Wozniak, and Ronald Wayne on April 1, 1976, 
in Cupertino, California. Tim Cook became the CEO of Apple in 2011 after Steve Jobs resigned. 
Apple developed the iPhone in 2007, which revolutionized the smartphone industry.

Microsoft Corporation was founded by Bill Gates and Paul Allen on April 4, 1975, in Albuquerque, 
New Mexico. Satya Nadella became the CEO of Microsoft in 2014. Microsoft acquired LinkedIn in 2016 
for $26.2 billion and GitHub in 2018 for $7.5 billion. Microsoft is headquartered in Redmond, Washington.

Google was founded by Larry Page and Sergey Brin in 1998 while they were PhD students at 
Stanford University. Sundar Pichai became the CEO of Google in 2015 and also became CEO of 
Alphabet Inc., Google's parent company, in 2019. Google is headquartered in Mountain View, California.

Amazon was founded by Jeff Bezos on July 5, 1994, in Bellevue, Washington. Andy Jassy became 
the CEO of Amazon in 2021 when Jeff Bezos stepped down. Amazon acquired Whole Foods Market in 2017 
for $13.7 billion. Amazon Web Services (AWS) was launched in 2006.

Tesla was founded by Martin Eberhard and Marc Tarpenning in 2003. Elon Musk joined Tesla as 
chairman of the board in 2004 and became CEO in 2008. Tesla is headquartered in Austin, Texas. 
Elon Musk also founded SpaceX in 2002 and co-founded OpenAI in 2015.

NVIDIA Corporation was founded by Jensen Huang, Chris Malachowsky, and Curtis Priem in 1993. 
Jensen Huang serves as the President and CEO of NVIDIA. NVIDIA is headquartered in Santa Clara, 
California. NVIDIA developed the CUDA platform which is widely used for AI and machine learning.

Meta Platforms (formerly Facebook) was founded by Mark Zuckerberg and his college roommates 
Eduardo Saverin, Andrew McCollum, Dustin Moskovitz, and Chris Hughes in 2004 at Harvard University. 
Meta acquired Instagram in 2012 for approximately $1 billion and WhatsApp in 2014 for $19 billion.

OpenAI was founded in December 2015 by Sam Altman, Elon Musk, Greg Brockman, Ilya Sutskever, 
and others. Sam Altman serves as the CEO of OpenAI. OpenAI released GPT-3 in 2020 and ChatGPT 
in November 2022. OpenAI is headquartered in San Francisco, California.
""")

    # Sample AI research article
    with open("demo_docs/ai_research.txt", "w", encoding="utf-8") as f:
        f.write("""Artificial Intelligence Research Milestones

The field of artificial intelligence was formally founded at the Dartmouth Conference in 1956, 
organized by John McCarthy, Marvin Minsky, Claude Shannon, and Nathaniel Rochester.

Geoffrey Hinton, Yann LeCun, and Yoshua Bengio received the 2018 Turing Award for their 
contributions to deep learning. Geoffrey Hinton worked at Google for over a decade before 
leaving in 2023. Yann LeCun is the Chief AI Scientist at Meta.

Transformer architecture was introduced by researchers at Google Brain in the paper 
"Attention Is All You Need" published in 2017. Ashish Vaswani, Noam Shazeer, Niki Parmar, 
and Jakob Uszkoreit were among the authors.

DeepMind was founded by Demis Hassabis, Shane Legg, and Mustafa Suleyman in London in 2010. 
Google acquired DeepMind in 2014 for approximately 500 million dollars. DeepMind developed 
AlphaGo which defeated world Go champion Lee Sedol in 2016. AlphaFold, developed by DeepMind, 
solved the protein folding problem in 2020.

Anthropic was founded in 2021 by Dario Amodei, Daniela Amodei, and other former OpenAI members. 
Dario Amodei serves as the CEO of Anthropic. Anthropic developed the Claude AI assistant. 
Anthropic is headquartered in San Francisco, California. Amazon invested $4 billion in Anthropic in 2023.

Hugging Face was founded by Clément Delangue, Julien Chaumond, and Thomas Wolf in 2016 in New York. 
Hugging Face is known for its Transformers library and the Model Hub platform. Hugging Face raised 
$235 million in funding in 2023 at a $4.5 billion valuation.

The ImageNet Large Scale Visual Recognition Challenge (ILSVRC) was organized by Fei-Fei Li at 
Stanford University. AlexNet, developed by Alex Krizhevsky, Ilya Sutskever, and Geoffrey Hinton 
at the University of Toronto, won the 2012 ImageNet competition and sparked the deep learning revolution.
""")

    print("✅ Demo documents created in demo_docs/")
    print("   - demo_docs/tech_companies.txt")
    print("   - demo_docs/ai_research.txt")


if __name__ == "__main__":
    create_demo_docs()
