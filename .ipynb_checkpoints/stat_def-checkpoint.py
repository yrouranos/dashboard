# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# Climate information dashboard.
# 
# Class definition: Stat and Stats.
#
# Contributors:
# 1. rousseau.yannick@ouranos.ca
# (C) 2021 Ouranos Inc., Canada
# ----------------------------------------------------------------------------------------------------------------------

import config as cf
import object_def
        
mode_min = "min"
mode_max = "max"
mode_mean = "mean"
mode_q_low = "q" + cf.q_low
mode_q_high = "q" + cf.q_high

code_desc = {
    mode_min: "Minimum",
    mode_max: "Maximum",
    mode_mean: "Moyenne",
    mode_q_low: cf.q_low + "e percentile",
    mode_q_high: cf.q_high + "e percentile"
}


class Stat(object_def.Obj):

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object Stat.
    --------------------------------------------------------------------------------------------------------------------
    """
    
    # Contructor.
    def __init__(self, code):
        desc = "" if code == "" else code_desc[code]
        super(View, self).__init__(code=code, desc=desc)

class Stats(object_def.Objs):

    """
    --------------------------------------------------------------------------------------------------------------------
    Class defining the object Stats.
    --------------------------------------------------------------------------------------------------------------------
    """

    # Constructors.
    def __init__(self, *args):
        super(Stats, self).__init__()
        
        if len(args) == 1:
            if isinstance(args[0], str) or isinstance(args[0], list):
                self.add(args[0])
            else:
                self.load(args)

    def load(self, args):

        """
        Load items.
        
        Parameters
        ----------
        args :
            args[0] = cntx : context_def.Context
                Context.
        """
        
        p = cf.d_map + "<varidx_code>/<hor>/<varidx_name>_<rcp>_<hor_>_<stat>_<delta>.csv"
        p = p.replace("<varidx_code>", cntx.varidx.get_code())
        p = p.replace("<varidx_name>", cntx.varidx.get_code())
        p = p.replace("<rcp>", cntx.rcp.get_code())
        p = p.replace("<hor_>", cntx.hor.get_code().replace("-", "_"))
        p = p.replace("<hor>", cntx.hor.get_code())
        p = p.replace("_<delta>", "" if cntx.delta is False else "_delta"        
        
        code_l = []
        for code in list(code_desc.keys()):
            if os.path.exists(p_templ.replace("<stat>", code)):
                code_l.append(code)

        self.add(code_l)

    def add(
        self,
        code: Union[str, List[str]],
        inplace: bool = True
    ):

        """
        Add one or several items.

        Parameters
        ----------
        code : Union[str, List[str]]
            Code or list of codes.
        inplace : bool
            If True, modifies the current instance.
        """

        code_l = code
        if isinstance(code, str):
            code_l = [code]

        items = []
        for i in range(len(code_l)):
            items.append(Stat(code_l[i]))

        return super(Stats, self).add_items(items, inplace)
