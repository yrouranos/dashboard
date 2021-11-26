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

import config as cf
import glob
import pandas as pd
import utils
from typing import List, Optional, Union

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

# Name-description associations:
name_desc = {rcp_ref: "Référence",
             rcp_26: "RCP 2.6",
             rcp_45: "RCP 4.5",
             rcp_85: "RCP 8.5",
             rcp_xx: "Tous"}

# RCP-colour associations.
rcp_color = {"ref": "black", "rcp26": "blue", "rcp45": "green", "rcp85": "red", "rcpxx": "pink"}


class RCP:

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining a RCP.
    --------------------------------------------------------------------------------------------------------------------
    """
    
    # Name.
    name = ""
    
    # Contructor.
    def __init__(self, name):
        self.name = name 

    def get_name(
        self
    ) -> str:
        
        """
        Get name.
        
        Returns
        -------
        str
            Name.
        """
            
        return self.name
    
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
            
        return name_desc[self.name]
    
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
            
        return rcp_color[self.name]
                         
    def copy(
        self
    ):
        
        """
        Copy object.
        
        Returns
        -------
        RCP
            Copy of current instance.
        """
        
        new = RCP(self.name)
        
        return new
    

class RCPs:

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining a list of RCPs.
    --------------------------------------------------------------------------------------------------------------------
    """
    
    # List of RCP instances.
    items = []

    # Constructors.
    def __init__(self, *args):
        
        if len(args) == 0:
            self.items = []
        
        else:
            self.load(args)
            
    def load(self, args):

        """
        Load items.

        Parameters
        ----------
        args :
            args[0] = d_data = Base directory of data.
            args[1] = varidx_code : str
                      Climate variable or index.
            args[2] = view : str
                      View = {"ts", "tbl", "map"}
            args[3] = hor : Optional[str]
                      Horizon (ex: "1981-2010")
        """

        d_data = args[0]
        varidx_code = args[1]
        view = args[2]
        hor = ""
        if len(args) > 3:
            hor = args[3]

        name_l = []

        # The list of RCPs is within data files.
        if view in ["ts", "tbl"]:
            p = d_data + "<view>/<varidx_code>.csv"
            p = p.replace("<view>", view)
            p = p.replace("<varidx_code>", varidx_code)
            df = pd.read_csv(p)
            if view == "ts":
                name_l = list(df.columns)
            else:
                name_l = df["rcp"]

        # The list of RCPs is within file structure.
        else:
            p = d_data + "<view>/<varidx_code>/<hor>/*.csv"
            p = p.replace("<view>", view)
            p = p.replace("<varidx_code>", varidx_code)
            p = p.replace("<hor>", hor)
            name_l = list(glob.glob(p))

        # Extract RCPs.
        name_clean_l = []
        for name in name_l:
            if ("rcp" in name) or (rcp_ref in name):
                name = name.split("_")[0 if view in ["ts", "tbl"] else 1]
                if name not in name_clean_l:
                    name_clean_l.append(name)
        name_clean_l.sort()

        # Create instances.
        self.items = []
        if rcp_ref in name_clean_l:
            self.items.append(RCP(rcp_ref))
        for name in name_clean_l:
            if name != rcp_ref:
                self.items.append(RCP(name))
    
    def add(
        self,
        name: Union[str, List[str]]
    ):
        
        """
        Add RCP.
        
        Paramters
        ---------
        name : Union[str, List[str]]
            Name or list of names.
        """        
        
        name_l = name
        if isinstance(name, str):
            name_l = [name]
        
        new = RCPs()
        for i in range(len(name_l)):
            new.items.append(RCP(name_l[i]))
        
        return new
    
    def remove(
        self,
        name: Union[str, List[str]]
    ):
        
        """
        Remove RCP.
        
        Paramters
        ---------
        name : Union[str, List[str]]
            Name or list of names.
        """
        
        name_l = name
        if isinstance(name, str):
            name_l = [name]
        
        new = self.copy()
        for i in range(len(name_l)):
            for j in range(len(new.items)):
                if new.items[j].name == name:
                    del new.items[j]
                    break
        
        return new
    
    def copy(
        self
    ):
        
        """
        Copy object.
        """
        
        new = RCPs()
        for item in self.items:
            new.items.append(RCP(item.name))
        
        return new
    
    def get_name(
        self,
        desc: str
    ) -> str:

        """
        Get name.

        Paramters
        ---------
        desc : str
            Description.

        Returns
        -------
        str
            Name.
        """    

        for item in self.items:
            if item.get_desc() == desc:
                return item.name

        return ""


    def get_desc(
        self,
        name: str
    ) -> str:

        """
        Get description.

        Paramters
        ---------
        name : str
            Name.

        Returns
        -------
        str
            Description.
        """    

        for item in self.items:
            if item.get_name() == name:
                return item.desc  

        return ""


    def get_name_l(
        self
    ) -> List[str]:
    
        """
        Get names.
    
        Returns
        -------
        List[str]
            Names.
        """
    
        name_l = []
    
        for item in self.items:
            name_l.append(item.get_name())
    
        return name_l
    
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
    