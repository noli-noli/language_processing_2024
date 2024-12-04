# Collaborative_classes_2024
本リポジトリは、2024年度社会人講座向けの教材として作成されたものである。
LLaMA2とLLaMA-Indexを使用してRetrieval Augmented Generation(RAG)を構築し、それをRestfull api経由で利用する。

## 具体的な機能
以下にリストアップする全ての機能をRestfull apiで使用する事が可能。
1. コンテキストをベクトルデータベースに変換しダウンロード
2. 作成したベクトルデータベースをアップロードする事で個別にセッションを構築
3. RAG有り・無しで推論結果を比較する
4. LLMによる推論結果の自動和訳
