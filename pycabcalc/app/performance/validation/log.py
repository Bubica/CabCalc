
class Logger(object):
    
    """
    A singleton instance.
    Class used for logging the validation results in the log file.
    Responsible for preserving the file format.
    """

    fname = None
    _logger = None    

    def __init__(self, fname):
        self._set_file(fname)
        self._reset()

    def __new__(class_, *args, **kwargs):
        """ Singleton """
        if not isinstance(class_._logger, class_) or (class_._logger.fname is not None and len(args)>0 and class_._logger.fname !=args[0]):
            class_._logger = object.__new__(class_, *args, **kwargs)
        return class_._logger

    def _reset(self):
        self.exp_setup = None   # experimental setup (route, area size etc), can be either a dictionary or pandas Series object
        self.model_setup = None # model setup (type, model related parameters)
        self.results = None # results of validation

    def _set_file(self, fname):
        self.fname = fname
        self.f = open(self.fname, "a")
        self._reset()

    # def _set_exp_setup(self, setup):
    #     self.exp_setup = setup
    #     self.model_setup = None
    #     self.results = None

    # def _set_model_setup(self, setup):
    #     """ Resets only parameters that are related to the model, not the route and experimental setup """
    #     self.model_setup = setup
    #     self.results = None
    
    def set_setup(self, expSetup, modelSetup):
        self.exp_setup = expSetup
        self.model_setup = modelSetup
        self.results = None

    def set_results(self, results):
        self.results = results

    def check_setup_logged(self):
        
        """ Checks if the setup has been already logged """

        line = self._setup_log_line()+self._model_log_line()
        ff = open(self.fname, 'r')
        s = ff.read()
        ff.close()

        if s.find(line)>-1: #finds a substring in a string
            return True
        else: 
            return False


    def _setup_log_line(self):

        """ Logs basic setup data and model type """

        s = ""
        s += str(self.exp_setup["from"]) + "|"
        s += str(self.exp_setup["to"]) + "|"
        s += str(self.exp_setup["date"]) + "|"
        s += str(self.exp_setup["train_time_interval"]) + "|"
        s += str(self.exp_setup["test_time_interval"]) + "|"
        s += str(self.exp_setup["train_sample_cnt"]) + "|"
        s += str(self.exp_setup["test_sample_cnt"]) + "|"
        s += str(self.exp_setup["train_area"]) + "|"
        s += str(self.exp_setup["test_area"]) + "|"
        s += str(self.exp_setup["estimator"]) + "|"


        return s

    def _model_log_line(self):

        """ Logs model parameters """

        s = ""
        s += str(self.model_setup["type"]) + "|"
        if "n_estimators" in s: s += str(self.model_setup["n_estimators"]) 
        s+=  "|"
        if "learn_rate" in s: s += str(self.model_setup["learn_rate"])
        s+=  "|"
        if "max_samples" in s: s += str(self.model_setup["max_samples"])
        s+=  "|"
        if "max_depth" in s: s += str(self.model_setup["max_depth"])
        s+=  "|"

        return s

    def _result_log_line(self):

        """ Logs the error (i.e. the result) of prediction """

        s = ""
        s += str(self.results["rmse"]) + "|"
        s += str(self.results["r2"]) + "|"
        s += str(self.results["fe"])

        return s

    def log_comment(self, comment):
        """ Logs comments (in a separate line) prefixed with # character """
        self.f.write("#" + comment+"\n")
        self.f.flush()

    def log(self):
        
        """ Writes logged values into the file """

        s = ""
        s += self._setup_log_line()
        s += self._model_log_line()
        s += self._result_log_line()
        s += "\n"
        
        self.f.write(s)
        self.f.flush()
