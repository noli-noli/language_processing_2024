import requests
import re


#サーバURL
url = "http://133.89.6.54:"

#ポート番号
port = "49153"

#翻訳元の言語コード
input_code = "eng_Latn"

#翻訳先の言語コード
output_code = "jpn_Jpan"

#最大生成トークン数(MAX=1000がおススメ)
max_length = 500



def main():
    #text = input("Please input text: ")
    #if text == "":
    text = """## Question: ほげほげ株式会社の株価は

According to the information provided, the stock price of ほげほげ株式会社 (Hogehoge Co., Ltd.) is not mentioned. The information provided is about the company's overview, services, and project achievements, but not about its stock price. Therefore, I cannot answer this question.
Basedontheinformationprovided,IcananswerthefollowingquestionsQuestionほげほげ株式会社の株価はAccordingtotheinformationprovided,thestockpriceofほげほげ株式会社HogehogeCo.,Ltd.isnotmentioned.Theinformationprovidedisaboutthecompanysoverview,services,andprojectachievements,butnotaboutitsstockprice.Therefore,Icannotanswerthisquestion."""

    print(text)
    pattern = r'[^\w.,\u3000-\u30FF\u3040-\u309F\u4E00-\u9FFF]'
    text = re.sub(pattern, '', text)
    print(text)
    #textに翻訳したい文章を入れる
    try:
        response = requests.get(url + port + "/text/?text=" + text + "&input_code=" + input_code + "&output_code=" + output_code + "&max_length=" + str(max_length) )
        print("input text:" + text.replace("\n",""))
        print("response text: " + response.text)
    except Exception as e:
        print("Error: ", e)



if __name__ == "__main__":
    main()