import os
import json
import requests

access_token = "qjEjdLSBKdmCBrbg44iWFKia23cQYvJL"

text = """
会社概要
ほげほげ株式会社は、革新的なテクノロジーとクリエイティブなアプローチを組み合わせ、顧客のビジネスを成功に導くことを使命としています。当社は2005年に設立され、以来、多くの企業や個人のニーズに応えてきました。

主なサービス
ITコンサルティング
ウェブ開発
アプリケーション開発
デジタルマーケティング
弊社の価値
ほげほげは、以下の価値観に基づいて事業を展開しています:

革新性: 常に最新のテクノロジーとトレンドに目を向け、クリエイティブなアプローチで問題に取り組みます。

信頼性: 顧客との信頼関係を大切にし、誠実さと透明性を守ります。

協力関係: チームワークと協力を重視し、共に成長するパートナーシップを築きます。

プロジェクト実績
当社はこれまでにさまざまな業界でプロジェクトを成功裏に遂行してきました。いくつかのハイライトをご紹介します:

大手小売企業向けのeコマースウェブサイトの開発
医療機器メーカー向けのクラウドベースのデータ管理システムの構築
スタートアップ企業向けのデジタルマーケティング戦略の立案と実行
お問い合わせ
お問い合わせやご相談は、下記の連絡先までお気軽にご連絡ください。

電話番号: 012-3456-7890
Eメール: hogehoge@hogehoge.hogehoge
"""

context = { "key": access_token , "context": text}

with open("context.json", "w") as f:
    json.dump(context, f, indent=4)

json_file = json.load(open("context.json", "r"))

url = "http://127.0.0.1:49152/schema_check/"

files = {'file': open("context.json", 'rb')}
response = requests.post(url, files=files)

print(response.text)