#! /usr/bin/env python
#

import numpy as np


__all__ = ["load_snidreader", "get_snidread"]

def load_snidreader(filename, targetname=None):
    """ Loads a snid.output file and returns a SNIDReader object """
    return SNIDReader.load(filename, targetname)


def get_snidread( snid_dataframe, targetname=None):
    """ Inputs a Panda DataFrame Containing the SNID output and returns a SNIDReader object
    (see load_snidreader if you what to directly load a snid.output file) 
    """
    return SNIDReader(snid_dataframe, targetname)


def load_snid_output(filename ):
    """ Load a snid.output file and returns a pandas DataFrame of the best matches """
    import pandas
    f = open(filename).read().split("### rlap-ordered template listings ###")[-1].splitlines()
    return pandas.DataFrame([l.split() for l in f[2:]], columns=f[1][1:].split())

#############################
#                           #
#   SNID Reader             #
#                           #
#############################

class SNIDReader( object ):

    CATEGORIES = {  "Ib":"Ib,Ib-norm,Ib-pec,IIb".split(","),
                    "Ia":"Ia,Ia-norm,Ia-91T,Ia-91bg,Ia-csm,Ia-pec,Ia-99aa,Ia-02cx".split(","),
                    "Ic":"Ic,Ic-norm,Ic-pec,Ic-broad".split(","),
                    "II":"II,IIP,II-pec,IIn,IIL".split(","),
                    "NotSN":"AGN,Gal,LBV,M-star,QSO,C-star".split(",")
                 }
    
    # ================ #
    #  I/O Methods     #
    # ================ #
    def __init__(self, snid_dataframe, targetname="NoName"):
        """ """
        self.set_snid_dataframe( snid_dataframe )
        self.set_targetname(targetname)
        
    @staticmethod
    def load(filein, targetname=None):
        """ read filein using snid_reader() and returns a loaded SNIDReader object"""
        snid = load_snid_output(filein)
        return SNIDReader(snid, targetname)
        
    def set_snid_dataframe(self, snid_dataframe):
        """ """
        self.data = snid_dataframe
        
    def set_targetname(self, targetname):
        """ """
        self._targetname = targetname
        
    # ================ #
    #  I/O Methods     #
    # ================ #
    def get_rlapvalues(self, nfirst=10, npfunc="mean", subtypeof=None):
        """ """
        self.nfirst = nfirst
        self.npfunc = npfunc
        return self.get_values(key="rlap", nfirst=nfirst, npfunc=npfunc, subtypeof=subtypeof)

    def get_values(self, key="rlap", nfirst=10, npfunc="mean", subtypeof=None):
        """ """

        values_key = np.asarray(self.data[key], dtype="float")
        dicval = {}
        if subtypeof is None:
            for t, tlist in self.CATEGORIES.items():
                flagin = np.in1d(self.types[:nfirst], tlist)
                dicval[t] = getattr(np, npfunc)(values_key[:nfirst][flagin]) if np.any(flagin) else 0
        else:
            for tlist in self.CATEGORIES[subtypeof]:
                flagin = np.in1d(self.types[:nfirst], [tlist])
                dicval[tlist] = getattr(np, npfunc)(values_key[:nfirst][flagin]) if np.any(flagin) else 0
        return dicval
    
    def show(self, savefile=None, highlight_subtype=False, nfirst=10, npfunc="mean",
                 **kwargs):
        """ 
        Parameters
        ----------
        highlight_subtype: [bool]
            If a type is highlighted (all analyzed entries correspond to this type), 
            you can vizualize the subclassification by setting this to True.

        
        """
        from .tools import spiderplot
        # Data
        dictvalues = self.get_rlapvalues(npfunc=npfunc,nfirst=nfirst) 
        values=[dictvalues[c] for c in self.categories]
        
        rarray = np.asarray([4, 8, 12, 16])
        if self.npfunc in ["nansum","sum"]:
            rarray *= self.nfirst
            
        # Spider Plot #
        dictout = spiderplot(self.categories, values, rarray=rarray, **kwargs)

        
        fig = dictout["fig"]
        ax  =  dictout["ax"]
        highlight = dictout["highlight"]
        if highlight is not None and highlight_subtype:
            htype = self.categories[highlight[0]]
            nsubtype = len(self.CATEGORIES[htype])
            labels   = self.CATEGORIES[htype]
            theta  = np.linspace(0.0, 2 * np.pi, nsubtype, endpoint=False) + (1-highlight[0])*np.pi/self.ncategories
            
            radii_dict_values = self.get_rlapvalues(subtypeof=htype)
            radii  = np.asarray([radii_dict_values[k] for k in labels])
            
            width_dict_values = self.get_values(subtypeof=htype, npfunc="sum", key="rlap")
            width  = np.asarray([width_dict_values[k] for k in labels]) / self.nfirst * 2*np.pi /180
            bars = ax.bar(theta, radii, width=width, bottom=0.0)
            
            colors = ["C%d"%i_ for i_ in range(nsubtype)]
            for r, bar, t, label_, color in zip(radii, bars, theta, labels, colors):
                if r==0: continue
                bar.set_facecolor(color)
                bar.set_alpha(0.5)
                ax.text(t, r*1.1, label_, color=color)

            

        
        # Additional Information #
        subtype, rlap, z, zerr = np.asarray(self.data[["type", "rlap", "z", "zerr"]][:1])[0]
        fig.text(0.5,0.98, "%s first entry:\n"%self.targetname+r"%s @ $z=%.3f \pm %.3f$ | rlap %.2f"%(subtype, float(z), float(zerr), float(rlap)), 
                        va="top",ha="center", fontsize="small", color="C0")
        # Name
        fig.text(0.5, 0.01, "%s rlap for the first %d entries"%(self.npfunc, self.nfirst), 
                        va="bottom",ha="center", fontsize="small", color="k", fontstyle="italic")

        if savefile:
            fig.savefig(savefile, dpi=150)
            
        return dictout


    # =================== #
    #   Properties        #
    # =================== #
    @property
    def ncategories(self):
        """ number of type categories """
        return len(self.categories)

    @property
    def categories(self):
        """ name of type categories """
        return np.asarray(list(self.CATEGORIES.keys()))
    
    @property
    def types(self):
        """ Matching types (sorted by rlap, see self.data)   """
        return np.asarray(self.data["type"], dtype="str")
    
    @property
    def rlaps(self):
        """ Matching rlaps (sorted by rlap, see self.data)   """
        return np.asarray(self.data["rlap"], dtype="float")
    
    @property
    def targetname(self):
        """ Name of the transient (if given, NoName otherwise) """
        if not hasattr(self, "_targetname") or self._targetname is None:
            self._targetname = "NoName"
        return self._targetname
