# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# Climate information dashboard.
# 
# Class definition: Obj and Objs.
#
# Contributors:
# 1. rousseau.yannick@ouranos.ca
# (C) 2021 Ouranos Inc., Canada
# ----------------------------------------------------------------------------------------------------------------------

import copy
from typing import List, Union


class Obj:

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object Obj.
    --------------------------------------------------------------------------------------------------------------------
    """
    
    # Code.
    code = ""

    # Description.
    desc = ""

    def __init__(self, code, desc):

        """
        ----------------------------------------
        Constructor.
        ----------------------------------------
        """

        self.code = code
        self.desc = desc

    def get_code(self) -> str:
    
        """
        ----------------------------------------
        Get code.

        Returns
        -------
        str
            Code.
        ----------------------------------------
        """

        return self.code

    def get_desc(self) -> str:

        """
        ----------------------------------------
        Get description.

        Returns
        -------
        str
            Description.
        ----------------------------------------
        """

        return self.desc

    def copy(self):

        """
        ----------------------------------------
        Copy instance.

        Returns
        -------
        View
            Copy of instance.
        ----------------------------------------
        """

        return copy.deepcopy(self)


class Objs:

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object Objs.
    --------------------------------------------------------------------------------------------------------------------
    """
    
    # List of instances.
    items = []

    def __init__(self, *args):

        """
        ----------------------------------------
        Constructor.
        ----------------------------------------
        """

        self.items = []

    def set_items(self, items):

        """
        ----------------------------------------
        Set items.
        ----------------------------------------
        """

        self.items = items

    def get_items(self):

        """
        ----------------------------------------
        Get items.
        ----------------------------------------
        """
        return self.items

    def get_code(self, desc: str) -> str:

        """
        ----------------------------------------
        Get code.

        Paramters
        ---------
        desc : str
            Description.

        Returns
        -------
        str
            Code.
        ----------------------------------------
        """

        for item in self.items:
            if item.get_desc() == desc:
                return item.code

        return ""

    def get_desc(self, code: str) -> str:

        """
        ----------------------------------------
        Get description.

        Paramters
        ---------
        code : str
            Code.

        Returns
        -------
        str
            Description.
        ----------------------------------------
        """

        for item in self.items:
            if item.get_code() == code:
                return item.desc

        return ""

    def get_code_l(self) -> List[str]:

        """
        ----------------------------------------
        Get a list of codes.

        Returns
        -------
        List[str]
            Codes.
        ----------------------------------------
        """

        code_l = []

        for item in self.items:
            code_l.append(item.get_code())

        return code_l

    def get_desc_l(self) -> List[str]:

        """
        ----------------------------------------
        Get a list of descriptions.

        Returns
        -------
        List[str]
            Descriptions.
        ----------------------------------------
        """

        desc_l = []

        for item in self.items:
            desc_l.append(item.get_desc())

        return desc_l

    def add_items(
        self,
        items: [any],
        inplace: bool = True
    ):

        """
        ----------------------------------------
        Add one or several items.

        Paramters
        ---------
        items : Union[any, List[any]]
            Item or list of items.
        inplace : bool
            If True, modifies the current instance.
        ----------------------------------------
        """

        new = self.copy()
        new.items = new.items + items
        if inplace:
            self.items = new.items
        else:
            return new

    def remove_items(
        self,
        code: Union[str, List[str]],
        inplace: bool = True
    ):

        """
        ----------------------------------------
        Remove one or several items (based on code).

        Paramters
        ---------
        code : Union[str, List[str]]
            Code or list of codes.
        inplace : bool
            If True, modifies the current instance.
        ----------------------------------------
        """

        code_l = code
        if isinstance(code, str):
            code_l = [code]

        new = copy.copy(self)
        for i in range(len(code_l)):
            for j in range(len(new.items)):
                if new.items[j].code == code:
                    del new.items[j]
                    break

        if inplace:
            self.items = new.items
        else:
            return new

    def copy(self):

        """
        ----------------------------------------
        Copy instance.

        Returns
        -------
        View
            Copy of instance.
        ----------------------------------------
        """

        return copy.deepcopy(self)
