# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# Climate information dashboard.
# 
# Class definition: Hor and Hors.
#
# Contributors:
# 1. rousseau.yannick@ouranos.ca
# (C) 2021-2022 Ouranos Inc., Canada
# ----------------------------------------------------------------------------------------------------------------------

# External libraries.
import glob
import os
import pandas as pd
import re
from typing import Union, List

# Dashboard libraries.
from def_constant import const as c
from def_context import cntx
import dash_utils as du
import def_object


class Hor(def_object.Obj):

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object Hor.
    --------------------------------------------------------------------------------------------------------------------
    """
    
    def __init__(
        self,
        code: Union[str, int, float, List[Union[str, int, float]]]
    ):

        """
        ----------------------------------------
        Constructor.

        Parameters
        ----------
        code: Union[str, int, float, List[Union[str, int, float]]]
            Code. Ex: "1981*2010" or ["1981", "2010"] or [1981, 2010] or [1981.0, 2010.0] => "1981-2010"
                      "1981" or 1981 or 1981.0 or ["1981"] or [1981] or [1981.0]          => "1981-1981"
        ----------------------------------------
        """

        if isinstance(code, str):
            tokens = re.sub("[^0-9]", "-", code).split("-")
            code = []
            for i in range(len(tokens)):
                token = tokens[i]
                if token.isnumeric():
                    code.append(str(int(token)))
                    if len(code) >= 2:
                        break

        if isinstance(code, int) or isinstance(code, float):
            code = [str(int(code))] * 2

        if isinstance(code, List):
            code_1 = "" if len(code) < 1 else code[0]
            code_2 = "" if len(code) < 2 else code[1]
            code = [code_1, code_2]
            for i in range(len(code)):
                try:
                    code[i] = str(int(code[i]))
                except ValueError:
                    code[i] = ""
            if (code[0] != "") or (code[1] != ""):
                if code[0] == "":
                    code[0] = code[1]
                if code[1] == "":
                    code[1] = code[0]
                code = code[0] + "-" + code[1]
            else:
                code = ""
        else:
            code = ""

        super(Hor, self).__init__(code=code, desc=code)

    @property
    def year_l(
        self
    ) -> List[int]:

        """
        ----------------------------------------
        Get years.

        Returns
        -------
        List[int]
            Years.
        ----------------------------------------
        """

        year_l = []

        tokens = self.code.split("-")
        for i in range(2):
            if len(tokens) >= i + 1:
                token = tokens[i]
                if token.isnumeric():
                    year_l.append(int(token))
                else:
                    year_l.append(-1)

        return year_l

    @property
    def year_1(
        self
    ) -> int:

        """
        ----------------------------------------
        Get first year.

        Returns
        -------
        int
            First year.
        ----------------------------------------
        """

        return self.year_l[0]

    @property
    def year_2(
            self
    ) -> int:

        """
        ----------------------------------------
        Get second year.

        Returns
        -------
        int
            Second year.
        ----------------------------------------
        """

        return self.year_l[1]


class Hors(def_object.Objs):

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object Hors.
    --------------------------------------------------------------------------------------------------------------------
    """

    def __init__(
        self,
        *args
    ):

        """
        ----------------------------------------
        Constructor.
        ----------------------------------------
        """

        super(Hors, self).__init__()

        if len(args) == 1:
            if args[0] == "*":
                self.load()
            else:
                self.add(args[0])

    def load(
        self
    ):

        """
        ----------------------------------------
        Load items.
        ----------------------------------------
        """

        code_l = []

        # Codes.
        view_code  = cntx.view.code if cntx.view is not None else ""
        vi_code    = cntx.varidx.code if cntx.varidx is not None else ""
        delta_code = cntx.delta.code if cntx.delta is not None else False

        # The items are extracted from directory names.
        # ~/<project_code>/map/<vi_code>/*
        if view_code == c.view_map:
            p = cntx.d_project + "<view>/<vi_code>/*/*_<delta>.csv"
            p = p.replace("<view>", view_code)
            p = p.replace("<vi_code>", vi_code)
            p = p.replace("_<delta>", "" if delta_code == "False" else "_delta")
            for p in glob.glob(p):
                code = os.path.basename(os.path.dirname(p))
                if code not in code_l:
                    code_l.append(code)

        # The items are extracted from the 'hor' column of data files.
        # ~/<project_code>/tbl/<vi_code>.csv
        elif view_code == c.view_tbl:
            df = pd.DataFrame(du.load_data())
            code_l = list(dict.fromkeys(list(df["hor"])))
            code_l.remove(df[df["rcp"] == c.ref]["hor"][0])

        # The items are extracted from directory names.
        # ~/<project_code>/cycle*/*
        elif view_code == c.view_cycle:
            p = cntx.d_project + "<view>/<vi_code>/*"
            p = p.replace("<view>/", view_code + "*/")
            p = p.replace("<vi_code>", vi_code)
            for p_i in list(glob.glob(p)):
                code = os.path.basename(p_i)
                if code not in code_l:
                    code_l.append(code)

        code_l.sort()

        # Remove the items that include all years. For instance, if the horizons are 1981-2010, 2021-2050, 2051-2080
        # and 1981-2080, the last horizon needs to be removed.
        if len(code_l) > 0:
            min_yr, max_yr = None, None
            for code in code_l:
                tokens = code.split("-")
                if min_yr is None:
                    min_yr = tokens[0]
                    max_yr = tokens[1]
                else:
                    min_yr = min(min_yr, tokens[0])
                    max_yr = max(max_yr, tokens[1])
            range_yr = min_yr + "-" + max_yr
            if range_yr in code_l:
                code_l.remove(range_yr)

        self.add(code_l)
            
    def add(
        self,
        item: Union[str, List[str], Hor],
        inplace: bool = True
    ):
        
        """
        ----------------------------------------
        Add one or several items.
        
        Parameters
        ----------
        item: Union[str, List[str], Hor]
            Item (code, list of codes or instance of Hor).
        inplace: bool
            If True, modifies the current instance.
        ----------------------------------------
        """        

        items = []

        if isinstance(item, Hor):
            items = [item]

        else:
            if not isinstance(item, List):
                code_l = [item]
            else:
                code_l = item
            for i in range(len(code_l)):
                items.append(Hor(code_l[i]))
        
        return super(Hors, self).add(items, inplace)
