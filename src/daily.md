* 行ったこと
    * 風景を顔の位置に合わせて追従させた
    * 風景画像の追従時に座標に移動平均フィルタを適用し，平滑化した
    * 風景画像をユーザから近い前景部分と背景部分に分けて，追従のときの移動度に差をつけた
    * 顔の位置がカメラの中央から上にいくほど，背景画像全体を垂直方向に拡大，下に行くほど縮小させた
    * (失敗)fpsを上げるために，顔追従と風景表示GUIを別プロセスで実行する

* 結果,考察
    * 背景部分は顔の垂直方向の位置によって，上ならば垂直方向に拡大，下ならば縮小すると，遠近感が生まれるように感じました．
    * 風景の画像であれば，顔の遠近による風景の変化は無視できる
    * 背景に対して，前景の移動は画像にもよりますが，1.1~1.3倍程度の移動度で良い.(移動度の差が大きいと違和感があり，かつ背景の重複部分が見えてしまう)

* 課題
    * fpsが十分に出ていない(マルチプロセスで子プロセスの顔トラッキングができなくなる)
    * 風景の3Dモデルを作らないまでも，背景画像を水平方向に丸めた円筒状にして歪ませるだけで，遠近感がより生まれる可能性がある(画像の端の方は顕著性が低いため)