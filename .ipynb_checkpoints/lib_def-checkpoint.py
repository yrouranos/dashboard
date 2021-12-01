# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# Climate information dashboard.
# 
# Class definition: Lib and Libs.
#
# Contributors:
# 1. rousseau.yannick@ouranos.ca
# (C) 2021 Ouranos Inc., Canada
# ----------------------------------------------------------------------------------------------------------------------

import object_def
import view_def
from typing import Union, List

mode_alt = "alt"
mode_hv = "hv"
mode_mat = "mat"

code_desc = {mode_alt: "altair",
             mode_hv: "hvplot",
             mode_mat: "matplotlib"}

class Lib(object_def.Obj):

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object Lib.
    --------------------------------------------------------------------------------------------------------------------
    """
    
    # Contructor.
    def __init__(self, code):
        super().__init__(code)

    def get_desc(
        self,
    ) -> str:
    
        """
        Get description.

        Returns
        -------
        str
            Description.
        """

        return code_desc[self.code]
    
    def copy(
        self
    ):
        
        """
        Copy item.
        
        Returns
        -------
        Lib
            Copy of item.
        """
        
        return Lib(self.code)
    
class Libs(object_def.Objs):

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object Libs.
    --------------------------------------------------------------------------------------------------------------------
    """
    
    # List of instances.
    items = []

    # Constructors.
    def __init__(self, *args):
        
        if len(args) == 0:
            self.items = []
        elif len(args) == 1:
            self.items = []
            code_l = []
            if args[0] == view_def.mode_ts:
                code_l = code_desc.get_keys()
            elif args[0] == view_def.mode_map:
                code_l = [code_desc[mode_alt]]
            self.add(code_l)

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
        
        new = Libs()
        for i in range(len(code_l)):
            new.items.append(Lib(code_l[i]))
        
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
        
        new = Libs()
        for item in self.items:
            new.items.append(Lib(item.code))
        
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
                return item.desc  

        return ""