# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# Climate information dashboard.
# 
# Class definition: RCP and RCPs.
#
# Contributors:
# 1. rousseau.yannick@ouranos.ca
# (C) 2021 Ouranos Inc., Canada
# ----------------------------------------------------------------------------------------------------------------------

import glob
import object_def
import pandas as pd
import view_def
from typing import List, Union

# Reference period.
rcp_ref = "ref"

# Future period RCP 2.6.
rcp_26 = "rcp26"

# Future period RCP 4.5.
rcp_45 = "rcp45"

# Future period RCP 8.5.
rcp_85 = "rcp85"

# Any type of RCP.
rcp_xx = "rcpxx"

# Properties of emission scenarios.
code_props = {rcp_ref: ["Référence", "black"],
              rcp_26: ["RCP 2.6", "blue"],
              rcp_45: ["RCP 4.5", "green"],
              rcp_85: ["RCP 8.5", "red"],
              rcp_xx: ["Tous", "pink"]}


class RCP(object_def.Obj):

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object RCP.
    --------------------------------------------------------------------------------------------------------------------
    """
    
    # Contructor.
    def __init__(self, code):
        super().__init__(code)
        self.code = code
    
    def get_desc(
        self
    ) -> str:
        
        """
        Get description.
        
        Returns
        -------
        str
            Description.
        """
            
        return code_props[self.code][0]
    
    def get_color(
        self
    ) -> str:
        
        """
        Get color.
        
        Returns
        -------
        str
            Color.
        """
            
        return code_props[self.code][1]
                         
    def copy(
        self
    ):
        
        """
        Copy item.
        
        Returns
        -------
        RCP
            Copy of item.
        """
        
        new = RCP(self.code)
        
        return new


class RCPs(object_def.Objs):

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object RCPs.
    --------------------------------------------------------------------------------------------------------------------
    """

    # Constructors.
    def __init__(self, *args):
        super().__init__()

        if len(args) == 1:
            self.items = self.add(args[0]).items
        elif len(args) > 1:
            self.load(args)

    def load(self, args):

        """
        Load items.

        Parameters
        ----------
        args :
            args[0] = cntx : cntx_def.Context
                Context.
            args[1] = d_data : str
                Base directory of data.)
        """

        cntx = args[0]
        d_data = args[1]

        # The list of RCPs is within data files.
        if cntx.view.get_code() in [view_def.mode_ts, view_def.mode_tbl]:
            p = d_data + "<view>/<varidx_code>.csv"
            p = p.replace("<view>", cntx.view.get_code())
            p = p.replace("<varidx_code>", cntx.varidx.get_code())
            df = pd.read_csv(p)
            if cntx.view.get_code() == view_def.mode_ts:
                code_l = list(df.columns)
            else:
                code_l = df["rcp"]

        # The list of RCPs is within file structure.
        else:
            p = d_data + "<view>/<varidx_code>/<hor>/*.csv"
            p = p.replace("<view>", cntx.view.get_code())
            p = p.replace("<varidx_code>", cntx.varidx.get_code())
            p = p.replace("<hor>", cntx.hor.get_code())
            code_l = list(glob.glob(p))

        # Extract RCPs.
        code_clean_l = []
        for code in code_l:
            if ("rcp" in code) or (rcp_ref in code):
                i_token = 0 if cntx.view.get_code() in [view_def.mode_ts, view_def.mode_tbl] else 1
                code = code.split("_")[i_token]
                if code not in code_clean_l:
                    code_clean_l.append(code)
        code_clean_l.sort()

        # Create items.
        self.items = []
        if rcp_ref in code_clean_l:
            self.items.append(RCP(rcp_ref))
        for code in code_clean_l:
            if code != rcp_ref:
                self.items.append(RCP(code))

    def add(
        self,
        code: Union[str, List[str]]
    ):

        """
        Add one or several items.

        Paramters
        ---------
        code : Union[str, List[str]]
            Code or list of codes.
        """

        code_l = code
        if isinstance(code, str):
            code_l = [code]

        new = RCPs()
        for i in range(len(code_l)):
            new.items.append(RCP(code_l[i]))

        return new

    def remove(
        self,
        code: Union[str, List[str]]
    ):
        
        """
        Remove one or several items.
        
        Paramters
        ---------
        code : Union[str, List[str]]
            Code or list of codes.
        """
        
        code_l = code
        if isinstance(code, str):
            code_l = [code]
        
        new = self.copy()
        for i in range(len(code_l)):
            for j in range(len(new.items)):
                if new.items[j].code == code:
                    del new.items[j]
                    break
        
        return new
    
    def copy(
        self
    ):
        
        """
        Copy items.
        """
        
        new = RCPs()
        for item in self.items:
            new.items.append(RCP(item.code))
        
        return new
    
    def get_code(
        self,
        desc: str
    ) -> str:

        """
        Get code.

        Paramters
        ---------
        desc : str
            Description.

        Returns
        -------
        str
            Code.
        """    

        for item in self.items:
            if item.get_desc() == desc:
                return item.code

        return ""

    def get_desc(
        self,
        code: str
    ) -> str:

        """
        Get description.

        Paramters
        ---------
        code : str
            Code.

        Returns
        -------
        str
            Description.
        """    

        for item in self.items:
            if item.get_code() == code:
                return item.get_desc()

        return ""

    def get_code_l(
        self
    ) -> List[str]:
    
        """
        Get codes.
    
        Returns
        -------
        List[str]
            Codes.
        """
    
        code_l = []
    
        for item in self.items:
            code_l.append(item.get_code())
    
        return code_l
    
    def get_desc_l(
        self
    ) -> List[str]:
    
        """
        Get descriptions.
    
        Returns
        -------
        List[str]
            Descriptions.
        """
    
        desc_l = []
    
        for item in self.items:
            desc_l.append(item.get_desc())
    
        return desc_l

    def get_color_l(
        self
    ) -> List[str]:
    
        """
        Get colors.
    
        Returns
        -------
        List[str]
            Colors.
        """
    
        color_l = []
    
        for item in self.items:
            color_l.append(item.get_color())
    
        return color_l
    