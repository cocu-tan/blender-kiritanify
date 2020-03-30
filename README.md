# blender-kiritanify

Add-on for editing niconico-style game play video in Blender: running voiceroid for voice synthesizing, creating captions, insert tachie (standing character images).

ニコ動スタイルのゲームプレイ実況動画を作るためのblender addonだよ、[SeikaCenter](https://hgotoh.jp/wiki/doku.php/documents/voiceroid/seikacenter/seikacenter-0010)経由でvoiceroidを叩いたり、キャプションを生成したり、立ち絵を突っ込んだりできるよ。

There are no guarantee about backward compatibility.

破壊的変更をする可能性があるので使うときは気をつけてね。無保証だよ。


## Feature
- セリフ関係
    - voiceroidをSeikaCenter経由で叩いて、音声ファイルを生成し、blender内のsound sequenceを追加
    - セリフからcaptionを生成して、blender内にimage sequenceを追加
- 立ち絵関係
    - ワンクリックで立ち絵をinsert
- 倍速関係
    - 倍速カットサポート
    - 倍速してるsequenceを正しい長さにする

## Installation guide
1. `git clone` this repository
2. Run `./package.sh`
3. Install `kiritanify.zip` in your blender
4. Install following libraries:
    - `pillow`
        - a.k.a PIL, for caption generation
    - `pydub`
        - for signal processing
    - `requests`
        - for http requests to seika center
5. Run blender 


### Install seika-center (Optional: if you want to use voiceroid)
**Technically background:** kiritanify uses SeikaCenter via HTTP protocol. Make sure your IP and local network settings. 

0. Install Kiritanify to blender 
1. Install [SeikaCenter](https://hgotoh.jp/wiki/doku.php/documents/voiceroid/seikacenter/seikacenter-0010)
2. Run SeikaCenter with `HTTP機能`.
3. Update ip address and user info in `SeikaCenterSetting` in `Kiritanify` pane in blender.




