# -*- coding: utf-8 -*-
"""
Created on Fri Dec 20 12:55:44 2019

@author: okawah

FdsHeader
    FDSファイルのヘッダー情報を保存するクラス
FdsHeaderAlias
    各言語でのエイリアス名を保存するクラス（構造体として使用）
loadFDS
    FDSファイルを読み込む関数
saveFDS
    FDSファイルに書き出す関数
loadFDS_DataList
    FDSファイルのうち、データリスト部分のみを読み込む関数

FD3ファイルも読み込み・書き込み可能
"""

from typing import Tuple
import re
import numpy as np


class InstrumentParameter:
    """InstrumentParameter
    2022 12 22 created"""

    def __init__(self) -> None:
        self.em_s_slit_ex = 0
        self.em_s_slit_em = 0
        self.em_s_pmtvolt = 0

        self.ex_s_slit_ex = 0
        self.ex_s_slit_em = 0
        self.ex_s_pmtvolt = 0

        self.em_l_slit_ex = 0
        self.em_l_slit_em = 0
        self.em_l_pmtvolt = 0

        self.ex_l_slit_ex = 0
        self.ex_l_slit_em = 0
        self.ex_l_pmtvolt = 0

    def output(self) -> str:
        _str = ""
        _slit_ex = "---" if self.ex_s_slit_ex == 0 else "{0:.1f}".format(self.ex_s_slit_ex)
        _slit_em = "---" if self.ex_s_slit_em == 0 else "{0:.1f}".format(self.ex_s_slit_em)
        _str += "\n励起側(200～500nm)  ｽﾘｯﾄ：{0}/{1}nm  ﾎﾄﾏﾙ電圧：{2:.0f}V".format(_slit_ex, _slit_em, self.ex_s_pmtvolt)
        _slit_ex = "---" if self.em_s_slit_ex == 0 else "{0:.1f}".format(self.em_s_slit_ex)
        _slit_em = "---" if self.em_s_slit_em == 0 else "{0:.1f}".format(self.em_s_slit_em)
        _str += "\n蛍光側(200～500nm)  ｽﾘｯﾄ：{0}/{1}nm  ﾎﾄﾏﾙ電圧：{2:.0f}V".format(_slit_ex, _slit_em, self.em_s_pmtvolt)
        _slit_ex = "---" if self.em_l_slit_ex == 0 else "{0:.1f}".format(self.em_l_slit_ex)
        _slit_em = "---" if self.em_l_slit_em == 0 else "{0:.1f}".format(self.em_l_slit_em)
        _str += "\n蛍光側(500～900nm)  ｽﾘｯﾄ：{0}/{1}nm  ﾎﾄﾏﾙ電圧：{2:.0f}V".format(_slit_ex, _slit_em, self.em_l_pmtvolt)
        _slit_ex = "---" if self.ex_l_slit_ex == 0 else "{0:.1f}".format(self.ex_l_slit_ex)
        _slit_em = "---" if self.ex_l_slit_em == 0 else "{0:.1f}".format(self.ex_l_slit_em)
        _str += "\n励起側(500～900nm)  ｽﾘｯﾄ：{0}/{1}nm  ﾎﾄﾏﾙ電圧：{2:.0f}V".format(_slit_ex, _slit_em, self.ex_l_pmtvolt)
        return _str


class FdsHeader:
    """
    FdsHeader
    FDSファイルのヘッダー情報を保存するためのクラス

    2022 12 21 MeasureDate, ShutterCtrl, Instrument added
    """

    def __init__(self):
        self.Language = "EN"

        self.SampleName = ""
        self.FileName = ""
        self.MeasureDate = ""
        self.Operator = ""
        self.Comment = ""

        self.Model = ""
        self.SerialNum = ""
        self.RomVer = ""
        self.Accessory = ""

        self.MeasType = ""
        self.ScanMode = ""
        self.DataMode = ""
        self.FixWL = 0
        self.ScanSpeed = 0
        self.ScanExStartWL = 0
        self.ScanEmStartWL = 0
        self.ScanExEndWL = 0
        self.ScanEmEndWL = 0
        self.ScanExStepWL = 0
        self.ScanEmStepWL = 0
        self.Delay = 0
        self.ExSlit = 0
        self.EmSlit = 0
        self.PMTVolt = 0
        self.ResponseAT = False
        self.CorrSpectra = False
        self.ShutterCtrl = False
        self.ContourStep = 0

        self.Instrument = InstrumentParameter()

    def show(self):
        import pprint
        pprint.pprint(vars(self))

    def parseString(self, attribute, String: str):
        """
        2020 01 09 文字列でのみ保持
        2022 12 21 CorrSpectra, ShutterCtrl, parse_instrument_param

        Parameters
        ----------
        attribute : TYPE
            DESCRIPTION.
        String : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """

        String = String.rstrip()
        if attribute == "CorrSpectra":
            String = String == "On"
        elif attribute == "ShutterCtrl":
            String = String == "On"
        else:
            # String = re.search(r'(.*) *\n', String).group()
            String = re.findall(r'(.*)\s*', String)[0]
            # if String[-1] == " ":
            #     String = String[:-1]

        setattr(self, attribute, String)

    def parse_instrument_param(self, line: str):
        line = line.rstrip()
        if line == "":
            return False
        _slit_ex = re.findall('ｽﾘｯﾄ：(.*?)/', line)[0]
        _slit_em = re.findall('/(.*?)nm', line)[0]
        _pmtvolt = re.findall('ﾎﾄﾏﾙ電圧：(.*?)V', line)[0]

        _slit_ex = 0 if _slit_ex == "---" else float(_slit_ex)
        _slit_em = 0 if _slit_em == "---" else float(_slit_em)
        _pmtvolt = float(_pmtvolt)

        if "励起側(200～500nm)" in line:
            self.Instrument.ex_s_slit_ex = _slit_ex
            self.Instrument.ex_s_slit_em = _slit_em
            self.Instrument.ex_s_pmtvolt = _pmtvolt
        if "蛍光側(200～500nm)" in line:
            self.Instrument.em_s_slit_ex = _slit_ex
            self.Instrument.em_s_slit_em = _slit_em
            self.Instrument.em_s_pmtvolt = _pmtvolt
        if "蛍光側(500～900nm)" in line:
            self.Instrument.em_l_slit_ex = _slit_ex
            self.Instrument.em_l_slit_em = _slit_em
            self.Instrument.em_l_pmtvolt = _pmtvolt
        if "励起側(500～900nm)" in line:
            self.Instrument.ex_l_slit_ex = _slit_ex
            self.Instrument.ex_l_slit_em = _slit_em
            self.Instrument.ex_l_pmtvolt = _pmtvolt
        return True


class FdsHeaderAlias():

    def __init__(self, lang="EN", bool_scan_mode_em=True):
        self.Language = lang

        if lang == "EN":
            self.SampleName = "Sample"
            self.FileName = "File name"
            self.MeasureDate = "Run date"
            self.Operator = "Operator"
            self.Comment = "Comment"

            self.Model = "Model"
            self.SerialNum = "Serial number"
            self.RomVer = "ROM Version"
            self.Accessory = "Accessory"

            self.MeasType = "Measurement type"
            self.ScanMode = "Scan mode"
            self.DataMode = "Data mode"
            self.FixWL = "EX WL" if bool_scan_mode_em else "EM WL"
            self.ScanExStartWL = "EX  Start WL"
            self.ScanEmStartWL = "EM  Start WL"
            self.ScanExEndWL = "EX  End WL"
            self.ScanEmEndWL = "EM  End WL"
            self.ScanExStepWL = "EX Sampling interval"
            self.ScanEmStepWL = "EM Sampling interval"
            self.ScanSpeed = "Scan speed"
            self.Delay = "Delay"
            self.ExSlit = "EX Slit"
            self.EmSlit = "EM Slit"
            self.PMTVolt = "PMT Voltage"
            self.ResponseAT = "Response"
            self.CorrSpectra = "Corrected spectra"
            self.ShutterCtrl = "Shutter Control"
            self.ContourStep = "Contour interval"

        elif lang == "JP":
            self.SampleName = "ｻﾝﾌﾟﾙ"
            self.FileName = "ﾌｧｲﾙ名"
            self.MeasureDate = "分析日時"
            self.Operator = "ｵﾍﾟﾚｰﾀ"
            self.Comment = "ｺﾒﾝﾄ"

            self.Model = "ﾓﾃﾞﾙ"
            self.SerialNum = "ｼﾘｱﾙ No."
            self.RomVer = "ROM Ver."
            self.Accessory = "ｵﾌﾟｼｮﾝ"

            self.MeasType = "測定ﾓｰﾄﾞ"
            self.ScanMode = "ｽｷｬﾝﾓｰﾄﾞ"
            self.DataMode = "ﾃﾞｰﾀﾓｰﾄﾞ"
            self.FixWL = "励起波長" if bool_scan_mode_em else "蛍光波長"
            self.ScanExStartWL = "励起開始波長"
            self.ScanEmStartWL = "蛍光開始波長"
            self.ScanExEndWL = "励起終了波長"
            self.ScanEmEndWL = "蛍光終了波長"
            self.ScanExStepWL = "励起側ｻﾝﾌﾟﾘﾝｸﾞ間隔"
            self.ScanEmStepWL = "蛍光側ｻﾝﾌﾟﾘﾝｸﾞ間隔"
            self.ScanSpeed = "ｽｷｬﾝｽﾋﾟｰﾄﾞ"
            self.Delay = "初期(安定)待ち時間"
            self.ExSlit = "励起側ｽﾘｯﾄ"
            self.EmSlit = "蛍光側ｽﾘｯﾄ"
            self.PMTVolt = "ﾎﾄﾏﾙ電圧"
            self.ResponseAT = "ﾚｽﾎﾟﾝｽ"
            self.CorrSpectra = "ｽﾍﾟｸﾄﾙ補正"
            self.ShutterCtrl = "ｼｬｯﾀ制御"
            self.ContourStep = "等高線間隔"


def loadFDS(path: str) -> Tuple[np.ndarray, np.ndarray, FdsHeader]:
    header = FdsHeader()

    flag_data = False
    flag_inst = False

    with open(path, "r") as f:
        lines = f.readlines()

    # 最初の一文字目で判断（手抜処理）
    # 対応言語が増えた場合に修正
    dict_lang = {'S': 'EN', 'ｻ': 'JP'}
    if lines[0][0] in dict_lang:
        alias = FdsHeaderAlias(dict_lang[lines[0][0]])
        header.Language = dict_lang[lines[0][0]]
    else:
        return None, None, None
    dict_alias = vars(alias)

    list_data = []

    for line in lines:
        # linesを一行ずつlineに格納して以下を実行
        if flag_data:  # もしデータリストだったら
            buff = line.split()  # 読み込んだ行を\t (タブスペースのこと)や\n（改行のこと）で分割
            if len(buff) == 0:
                continue
            if buff[0] == "nm":
                continue
            list_data.append(np.array(buff, dtype=float))
        elif flag_inst:
            flag_inst = header.parse_instrument_param(line)
        else:  # まだデータリストでなかったら
            if line.rstrip() == "ﾃﾞｰﾀﾘｽﾄ" or line.rstrip() == "Data points":
                flag_data = True
            elif line.rstrip() == "装置関数":
                flag_inst = True
            else:
                # ヘッダー読込
                _buf = line.split(':\t')
                _att = getKeyFromValue(dict_alias, _buf[0])
                if _att is not None and "ScanMode" in _att:
                    # TODO: これは突貫対応
                    # TODO: 英語版対応
                    if "蛍光" in _buf[1]:
                        dict_alias["FixWL"] = "励起波長"
                    if "励起" in _buf[1]:
                        dict_alias["FixWL"] = "蛍光波長"
                    if "Emission" in _buf[1]:
                        dict_alias["FixWL"] = "EX WL"
                    if "Excitation" in _buf[1]:
                        dict_alias["FixWL"] = "EM WL"
                if len(_buf) >= 2 and _att is not None and _buf[1] != '\n':
                    # print(_att, _buf[1])
                    # Avoid \n
                    header.parseString(_att, _buf[1])
    if header.MeasType == "波長ｽｷｬﾝ" or header.MeasType == "Wavelength scan":
        mat_data = np.stack(list_data)
        return mat_data[:, 0], mat_data[:, 1], header
    elif header.MeasType == "3次元" or header.MeasType == "3-D scan":
        wl_ex = list_data.pop(0)
        mat_data = np.stack(list_data)
        wl_em = mat_data[:, 0]
        data = mat_data[:, 1:]
        return (wl_ex, wl_em), data, header


def saveFDS(path: str, wl: np.ndarray, data: np.ndarray, header: FdsHeader) -> None:
    bool_scanmode_em = "蛍光" in header.ScanMode or "Em" in header.ScanMode
    alias = FdsHeaderAlias(header.Language, bool_scanmode_em)

    with open(path, mode='w') as f:
        f.write(alias.SampleName + ":\t" + header.SampleName + "\n")
        f.write(alias.FileName + ":\t" + header.FileName + "\n")
        f.write(alias.MeasureDate + ":\t" + header.MeasureDate + "\n")
        f.write(alias.Operator + ":\t" + header.Operator + "\n")
        f.write(alias.Comment + ":\t" + header.Comment + "\n")

        if header.Language == "EN":
            f.write("\nInstrument\n")
        elif header.Language == "JP":
            f.write("\n光度計\n")

        f.write(alias.Model + ":\t" + header.Model + "\n")
        f.write(alias.SerialNum + ":\t" + header.SerialNum + "\n")
        f.write(alias.RomVer + ":\t" + header.RomVer + "\n")
        if header.Accessory != "":
            f.write(alias.Accessory + ":\t" + header.Accessory + "\n")

        if header.Language == "EN":
            f.write("\nInstrument parameters\n")
        elif header.Language == "JP":
            f.write("\n装置条件\n")

        f.write(alias.MeasType + ":\t" + header.MeasType + "\n")
        if header.MeasType == "波長ｽｷｬﾝ" or header.MeasType == "Wavelength scan":
            f.write(alias.ScanMode + ":\t" + header.ScanMode + "\n")
        f.write(alias.DataMode + ":\t" + header.DataMode + "\n")
        if header.MeasType == "波長ｽｷｬﾝ" or header.MeasType == "Wavelength scan":
            f.write(alias.FixWL + ":\t" + header.FixWL + "\n")
            if header.ScanMode == "励起ｽﾍﾟｸﾄﾙ" or header.ScanMode == "Excitation":
                f.write(alias.ScanExStartWL + ":\t" + header.ScanExStartWL + "\n")
                f.write(alias.ScanExEndWL + ":\t" + header.ScanExEndWL + "\n")
            if header.ScanMode == "蛍光ｽﾍﾟｸﾄﾙ" or header.ScanMode == "Emission":
                f.write(alias.ScanEmStartWL + ":\t" + header.ScanEmStartWL + "\n")
                f.write(alias.ScanEmEndWL + ":\t" + header.ScanEmEndWL + "\n")
        elif header.MeasType == "3次元" or header.MeasType == "3-D scan":
            f.write(alias.ScanExStartWL + ":\t" + header.ScanExStartWL + "\n")
            f.write(alias.ScanExEndWL + ":\t" + header.ScanExEndWL + "\n")
            f.write(alias.ScanExStepWL + ":\t" + header.ScanExStepWL + "\n")
            f.write(alias.ScanEmStartWL + ":\t" + header.ScanEmStartWL + "\n")
            f.write(alias.ScanEmEndWL + ":\t" + header.ScanEmEndWL + "\n")
            f.write(alias.ScanEmStepWL + ":\t" + header.ScanEmStepWL + "\n")

        f.write(alias.ScanSpeed + ":\t" + header.ScanSpeed + "\n")
        if header.MeasType == "波長ｽｷｬﾝ" or header.MeasType == "Wavelength scan":
            f.write(alias.Delay + ":\t" + header.Delay + "\n")
        f.write(alias.ExSlit + ":\t" + header.ExSlit + "\n")
        f.write(alias.EmSlit + ":\t" + header.EmSlit + "\n")
        f.write(alias.PMTVolt + ":\t" + header.PMTVolt + "\n")
        f.write(alias.ResponseAT + ":\t" + header.ResponseAT + " \n")
        str_corrspectra = "On" if header.CorrSpectra else "Off"
        f.write(alias.CorrSpectra + ":\t" + str_corrspectra + "\n")
        if header.Language == "JP":
            str_shutterctrl = "On" if header.ShutterCtrl else "Off"
            f.write(alias.ShutterCtrl + ":\t" + str_shutterctrl + "\n")
        elif header.Language == "EN" and header.ShutterCtrl:
            f.write(alias.ShutterCtrl + ":\tOn\n")

        if header.MeasType == "3次元" or header.MeasType == "3-D scan":
            f.write(alias.ContourStep + ":\t" + header.ContourStep + "\n")

        if header.CorrSpectra and header.Language == "JP":
            f.write("\n装置関数")
            str_instrument = header.Instrument.output()
            f.write(str_instrument + "\n")

        if header.Language == "EN":
            f.write("\nData points\n")
        elif header.Language == "JP":
            f.write("\nﾃﾞｰﾀﾘｽﾄ\n")

        if header.MeasType == "波長ｽｷｬﾝ" or header.MeasType == "Wavelength scan":
            f.write("nm\tData\n")

        if header.MeasType == "波長ｽｷｬﾝ" or header.MeasType == "Wavelength scan":
            for wlwl in range(len(wl)):
                f.write("{:.1f}\t".format(wl[wlwl]))
                f.write(val2str(data[wlwl]) + "\n")
        if header.MeasType == "3次元" or header.MeasType == "3-D scan":
            for _wl_ex in wl[0]:
                f.write("\t{:.3f}".format(_wl_ex))
            f.write("\n")
            for _i_em in range(len(wl[1])):
                f.write("{:.1f}".format(wl[1][_i_em]))
                for _i_ex in range(len(wl[0])):
                    f.write("\t{}".format(val2str(data[_i_em, _i_ex])))
                f.write("\n")


def val2str(val):
    if val > 9999.8:
        return "9999.9"
    if val < 1000.0:
        _buf = "{:.6f}".format(float(val))
        if (_buf[0] != "-" and len(_buf) > 5 and _buf[5:].count(".") == 0):
            _buf = _buf[:5]
    else:
        _buf = "{:.0f}".format(float(val))
    return _buf


def getKeyFromValue(dic, val):
    keys = [k for k, v in dic.items() if v == val]
    if keys:
        return keys[0]
    return None


def loadFDS_DataList(path):
    """
    load only Datalist
    """

    flag_data = False

    with open(path, "r") as f:
        lines = f.readlines()

    wl = []    # 格納する変数を宣言
    data = []  # []は 中身のないリスト

    for line in lines:
        # linesを一行ずつlineに格納して以下を実行
        if flag_data:  # もしデータリストだったら
            buff = line.split()  # 読み込んだ行を\t (タブスペースのこと)や\n（改行のこと）で分割
            if len(buff) == 2:   # 要素数が2つなら（データリスト内は 波長\t透過率\t\n）で保存されている
                wl.append(float(buff[0]))    # 0番目の要素を数値と解釈してwlのリストに追加
                data.append(float(buff[1]))  # 1番目の要素を数値と解釈してdataのリストに追加
        else:  # まだデータリストでなかったら
            if line[:2] == "nm":  # その行の先頭2文字を確認して "nm" と一致するかチェック
                flag_data = True  # 一致してたらその次の行からデータリスト内と判断

    return np.asarray(wl), np.asarray(data)


if __name__ == "__main__":
    filepath = "testfile.TXT"
    wl, data, header = loadFDS(filepath)
    # header.show()
    # print("shape", wl_ex.shape, wl_em.shape, data.shape)
    saveFDS("./output/test.txt", wl, data, header)
