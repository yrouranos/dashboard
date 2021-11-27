# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# Climate information dashboard.
# 
# Class definition: View and Views.
#
# Contributors:
# 1. rousseau.yannick@ouranos.ca
# (C) 2021 Ouranos Inc., Canada
# ----------------------------------------------------------------------------------------------------------------------

import object_def
from typing import Union, List

mode_ts = "ts"
mode_tbl = "tbl"
mode_map = "map"

code_desc = {mode_ts: "Série temporelle",
             mode_tbl: "Tableau",
             mode_map: "Carte"}


class View(object_def.Obj):

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object View.
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
        View
            Copy of item.
        """
        
        return View(self.code)
    
class Views(object_def.Objs):

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object Views.
    --------------------------------------------------------------------------------------------------------------------
    """
    
    # List of instances.
    items = []

    # Constructors.
    def __init__(self, *args):
        
        if len(args) == 0:
            for code in list(code_desc.keys()):
                self.items.append(View(code))
        elif len(args) == 1:
            self = self.add(args[0])

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
        
        new = Views()
        for i in range(len(code_l)):
            new.items.append(View(code_l[i]))
        
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
        
        new = Views()
        for item in self.items:
            new.items.append(View(item.code))
        
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