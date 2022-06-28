# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# Climate information dashboard.
# 
# Class definition: Obj and Objs.
#
# Contributors:
# 1. rousseau.yannick@ouranos.ca
# (C) 2021-2022 Ouranos Inc., Canada
# ----------------------------------------------------------------------------------------------------------------------

# External libraries.
import copy
from typing import List, Union


class Obj:

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object Obj.
    --------------------------------------------------------------------------------------------------------------------
    """

    # Code.
    _code: str = ""

    # Description.
    _desc: str = ""

    def __init__(
        self,
        code: Union[str, bool],
        desc: str
    ):

        """
        ----------------------------------------
        Constructor.
        ----------------------------------------
        """

        self._code = code
        self._desc = desc

    @property
    def code(
        self
    ) -> str:
    
        """
        ----------------------------------------
        Get code.

        Returns
        -------
        str
            Code.
        ----------------------------------------
        """

        return self._code

    @code.setter
    def code(
        self,
        code: str
    ):

        """
        ----------------------------------------
        Set code.

        Parameters
        ----------
        code: str
            Code.
        ----------------------------------------
        """

        self._code = code

    @property
    def desc(
        self
    ) -> str:

        """
        ----------------------------------------
        Get description.

        Returns
        -------
        str
            Description.
        ----------------------------------------
        """

        return self._desc

    @desc.setter
    def desc(
        self,
        desc: str
    ):

        """
        ----------------------------------------
        Set description.

        Parameters
        ----------
        desc: str
            Description.
        ----------------------------------------
        """

        self._desc = desc

    def copy(
        self
    ):

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
    _items = []

    def __init__(
        self,
        *args
    ):

        """
        ----------------------------------------
        Constructor.
        ----------------------------------------
        """

        self._items = []

    def inst_from_code(
        self,
        code: str
    ) -> Union[Obj, None]:

        """
        ----------------------------------------
        Get an instance based on its code.

        Returns
        -------
        Obj
            Instance corresponding to the code.
        ----------------------------------------
        """

        for item in self._items:
            if item.code == code:
                return item.copy()

        return None

    @property
    def items(
        self
    ):

        """
        ----------------------------------------
        Get items.
        ----------------------------------------
        """
        return self._items

    @items.setter
    def items(
        self,
        items
    ):

        """
        ----------------------------------------
        Set items.
        ----------------------------------------
        """

        self._items = items

    @property
    def count(
        self
    ):

        """
        ----------------------------------------
        Get the number of items.
        ----------------------------------------
        """
        return len(self._items)

    def code_from_desc(
        self,
        desc: str
    ) -> Union[str, bool]:

        """
        ----------------------------------------
        Get code.

        Paramters
        ---------
        desc: str
            Description.

        Returns
        -------
        Union[str, bool]
            Code.
        ----------------------------------------
        """

        for item in self._items:
            if item.desc == desc:
                return item.code

        return ""

    def desc_from_code(
        self,
        code: str
    ) -> str:

        """
        ----------------------------------------
        Get description.

        Paramters
        ---------
        code: str
            Code.

        Returns
        -------
        str
            Description.
        ----------------------------------------
        """

        for item in self._items:
            if item.code == code:
                return item.desc

        return ""

    @property
    def code_l(
        self
    ) -> List[Union[str, bool]]:

        """
        ----------------------------------------
        Get a list of codes.

        Returns
        -------
        List[Union[str, bool]]
            Codes.
        ----------------------------------------
        """

        code_l = []

        for item in self._items:
            code_l.append(item.code)

        return code_l

    @property
    def desc_l(
        self
    ) -> List[str]:

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

        for item in self._items:
            desc_l.append(item.desc)

        return desc_l

    def add(
        self,
        items: Union[any, List[any]],
        inplace: bool = True
    ):

        """
        ----------------------------------------
        Add one or several items.

        Paramters
        ---------
        items: Union[any, List[any]]
            Item or list of items.
        inplace: bool
            If True, modifies the current instance.
        ----------------------------------------
        """

        if not isinstance(items, List):
            items = [items]

        new = self.copy()
        new.items = new.items + items
        if inplace:
            self._items = new.items
        else:
            return new

    def remove(
        self,
        code: Union[str, List[str]],
        inplace: bool = True
    ):

        """
        ----------------------------------------
        Remove one or several items (based on code).

        Paramters
        ---------
        code: Union[str, List[str]]
            Code or list of codes.
        inplace: bool
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
            self._items = new.items
        else:
            return new

    def copy(
        self
    ):

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
