import re
from pathlib import Path
import numpy as np
from module_fds import loadFDS, saveFDS, InstrumentParameter


def calibrate_matrix(
    mat_input: np.ndarray, vec_ex_input: np.ndarray, vec_em_input: np.ndarray,
    mat_calib: np.ndarray, vec_ex_calib: np.ndarray, vec_em_calib: np.ndarray
):
    # Emission matrix shape: (N, 1)
    # Excitation matrix shape: (1, N)

    _mat_calib = np.ones(mat_input.shape)
    for _iem in range(_mat_calib.shape[0]):
        for _iex in range(_mat_calib.shape[1]):
            _wl_em = vec_em_input if vec_em_input.size == 1 else vec_em_input[_iem]
            _wl_ex = vec_ex_input if vec_ex_input.size == 1 else vec_ex_input[_iex]
            if np.any(vec_em_calib == _wl_em) and np.any(vec_ex_calib == _wl_ex):
                _mat_calib[_iem, _iex] = mat_calib[vec_em_calib == _wl_em, vec_ex_calib == _wl_ex]
            else:
                _mat_calib[_iem, _iex] = 1

    return np.squeeze(mat_input * _mat_calib)


def make_inst_func_matrix(filepath_exs: str = None, filepath_ems: str = None, filepath_exl: str = None, filepath_eml: str = None):

    _inst = InstrumentParameter()

    list_wl_ex = []
    list_wl_em = []
    list_data_ex = []
    list_data_em = []

    if filepath_exs is not None:
        wl_exs, data_exs, header_exs = loadFDS(filepath_exs)
        wl_threshold = np.inf if filepath_exl is None else 500
        list_wl_ex.append(wl_exs[wl_exs <= wl_threshold])
        list_data_ex.append(data_exs[wl_exs <= wl_threshold])
        _inst.ex_s_slit_ex = float(re.findall("(.*) nm", header_exs.ExSlit)[0])
        _inst.ex_s_slit_em = float(re.findall("(.*) nm", header_exs.EmSlit)[0])
        _inst.ex_s_pmtvolt = float(re.findall("(.*) V", header_exs.PMTVolt)[0])

    if filepath_ems is not None:
        wl_ems, data_ems, header_ems = loadFDS(filepath_ems)
        wl_threshold = np.inf if filepath_eml is None else 500
        list_wl_em.append(wl_ems[wl_ems <= wl_threshold])
        list_data_em.append(data_ems[wl_ems <= wl_threshold])
        _inst.em_s_slit_ex = float(re.findall("(.*) nm", header_ems.ExSlit)[0])
        _inst.em_s_slit_em = float(re.findall("(.*) nm", header_ems.EmSlit)[0])
        _inst.em_s_pmtvolt = float(re.findall("(.*) V", header_ems.PMTVolt)[0])

    if filepath_exl is not None:
        wl_exl, data_exl, header_exl = loadFDS(filepath_exl)
        wl_threshold = -np.inf if filepath_exs is None else 500
        list_wl_ex.append(wl_exl[wl_exl > wl_threshold])
        list_data_ex.append(data_exl[wl_exl > wl_threshold])
        _inst.ex_l_slit_ex = float(re.findall("(.*) nm", header_exl.ExSlit)[0])
        _inst.ex_l_slit_em = float(re.findall("(.*) nm", header_exl.EmSlit)[0])
        _inst.ex_l_pmtvolt = float(re.findall("(.*) V", header_exl.PMTVolt)[0])

    if filepath_eml is not None:
        wl_eml, data_eml, header_eml = loadFDS(filepath_eml)
        wl_threshold = -np.inf if filepath_ems is None else 500
        list_wl_em.append(wl_eml[wl_eml > wl_threshold])
        list_data_em.append(data_eml[wl_eml > wl_threshold])
        _inst.em_l_slit_ex = float(re.findall("(.*) nm", header_eml.ExSlit)[0])
        _inst.em_l_slit_em = float(re.findall("(.*) nm", header_eml.EmSlit)[0])
        _inst.em_l_pmtvolt = float(re.findall("(.*) V", header_eml.PMTVolt)[0])

    wl_ex: np.ndarray = np.concatenate(list_wl_ex)
    wl_em: np.ndarray = np.concatenate(list_wl_em)
    data_ex = np.concatenate(list_data_ex)
    data_em = np.concatenate(list_data_em)

    data_eem: np.ndarray = np.dot(data_em[:, None], data_ex[None, :])

    return wl_ex, wl_em, data_eem, _inst


class Calibrator():
    inst: InstrumentParameter
    mat_inst_func: np.ndarray
    vec_wl_ex_inst: np.ndarray
    vec_wl_em_inst: np.ndarray
    flag_inst_func: bool
    flag_output_dir: bool
    output_dir: str

    def __init__(self) -> None:
        self.flag_inst_func = False
        self.flag_output_dir = False
        self.output_dir = ""

    def set_output_dir(self, dir_output):
        if dir_output is None:
            self.output_dir = ""
            self.flag_output_dir = False
            return
        self.output_dir = dir_output
        self.flag_output_dir = True

    def set_mat_inst_func(self, filepath_exs: str = None, filepath_ems: str = None, filepath_exl: str = None, filepath_eml: str = None):
        self.vec_wl_ex_inst, self.vec_wl_em_inst, self.mat_inst_func, self.inst = make_inst_func_matrix(filepath_exs, filepath_ems, filepath_exl, filepath_eml)
        self.flag_inst_func = True

    def clear_mat_inst_func(self):
        self.flag_inst_func = False

    def is_ready(self):
        return self.flag_inst_func and self.flag_output_dir

    def is_ready_detail(self):
        return self.flag_inst_func, self.flag_output_dir

    def calibrate(self, filepath_input, bool_off_to_on=None):
        if not self.flag_inst_func:
            raise ValueError("instrumental Function is not loaded")
        if not self.flag_output_dir:
            raise ValueError("output path is not selected")
        wl, data, header = loadFDS(filepath_input)

        if header.MeasType == "波長ｽｷｬﾝ" or header.MeasType == "Wavelength scan":
            fixwl = np.array(header.FixWL[:-3], dtype=float)

            if "蛍光" in header.ScanMode or "Em" in header.ScanMode:
                wl_ex = fixwl
                wl_em = wl
                data = data[:, None]
            if "励起" in header.ScanMode or "Ex" in header.ScanMode:
                wl_ex = wl
                wl_em = fixwl
                data = data[None, :]
        elif header.MeasType == "3次元" or header.MeasType == "3-D scan":
            wl_ex = wl[0]
            wl_em = wl[1]

        if bool_off_to_on is None:
            if header.CorrSpectra:
                _calib = 1 / self.mat_inst_func
            else:
                _calib = self.mat_inst_func
                header.Instrument = self.inst
        elif bool_off_to_on:
            _calib = self.mat_inst_func
            header.Instrument = self.inst
            header.CorrSpectra = False
        else:
            _calib = 1 / self.mat_inst_func
            header.CorrSpectra = True

        calibrated = calibrate_matrix(data, wl_ex, wl_em, _calib, self.vec_wl_ex_inst, self.vec_wl_em_inst)
        header.CorrSpectra = not header.CorrSpectra
        _corr = "_calib_on" if header.CorrSpectra else "_calib_off"
        saveFDS(
            Path(self.output_dir) / (Path(filepath_input).stem + _corr + Path(filepath_input).suffix),
            wl, calibrated, header
        )
        return Path(self.output_dir) / (Path(filepath_input).stem + _corr + Path(filepath_input).suffix)


if __name__ == "__main__":
    pass
