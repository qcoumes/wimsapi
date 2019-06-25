class ExerciseScore:
    """Used to store every kind of score of a WIMS Exercise received from ADM/RAW.

    The following table give the correspondense between WIMS, ADM/RAW's getsheetscores job,
    and wimsapi value:
        
            +-----------------+----------------+----------+
            |    Exercise     |    ADM/RAW     | WIMSAPI  |
            +-----------------+----------------+----------+
            | Points required | requires       | required |
            | Weigth          | weights        | weight   |
            | Quality         | mean_detail    | quality  |
            | Cumul           | got_detail     | cumul    |
            | Best scores     | best_detail    | best     |
            | Acquired        | level_detail   | acquired |
            | Last Result     | last_detail    | last     |
            | Number of tries | try_detail     | tries    |
            +-----------------+----------------+----------+

    Parameters:
        exo - (Exercise) Sheet corresponding to these scores.
        user - (User) Sheet corresponding to these scores.
        quality - (float) Quality score ([0, 10]) as given by WIMS.
        cumul - (float) Cumul score ([0, 100]) as given by WIMS.
        best - (float) Level of success ([0, 100]) as given by WIMS.
        acquired - (float) Acquisition score ([0, required]) as given by WIMS.
        last - (float) Last score obtained ([0, required]) as given by WIMS.
        weight - (int) Weight of the sheet in the Class' score.
        tries - (int) Number of try as given by WIMS."""
    
    
    def __init__(self, exo, user, quality, cumul, best, acquired, last, weight, tries, **kwargs):
        self.exo = exo
        self.user = user
        self.quality = quality
        self.cumul = cumul
        self.best = best
        self.acquired = acquired
        self.last = last
        self.weight = weight
        self.tries = tries



class SheetScore:
    """Used to store every kind of score of a WIMS Sheet received from ADM/RAW.
    
    The following table give the correspondense between WIMS, ADM/RAW's getsheetscores job,
    and wimsapi value:
            
            +-------------+--------------+----------+
            |    WIMS     |   ADM/RAW    | WIMSAPI  |
            +-------------+--------------+----------+
            | Score       |      ?       | score    |
            | Quality     | user_quality | quality  |
            | Cumul       | user_percent | cumul    |
            | Best scores | user_best    | best     |
            | Acquired    | user_level   | acquired |
            | Weigth      |      -       | weight   |
            +-------------+--------------+----------+
    
    Sheet's weight is not in getsheetscores, but can be obtain through getsheet.
    
    Parameters:
        sheet - (Sheet) Sheet corresponding to these scores.
        user - (User) Sheet corresponding to these scores.
        score - (float) Global score ([0, 10]) as given by WIMS.
        quality - (float) Quality score ([0, 10]) as given by WIMS.
        cumul - (float) Cumul score ([0, 100]) as given by WIMS.
        best - (float) Level of success ([0, 100]) as given by WIMS.
        acquired - (float) Acquisition score ([0, 10]) as given by WIMS.
        weight - (int) Weight of the sheet in the Class' score.
        exercises - (List[ExerciseScore]) List of the scores obtained for each exercises."""
    
    
    def __init__(self, sheet, user, score, quality, cumul, best, acquired, weight, exercises,
                 **kwargs):
        self.sheet = sheet
        self.user = user
        self.score = score
        self.quality = quality
        self.cumul = cumul
        self.best = best
        self.acquired = acquired
        self.weight = weight
        self.exercises = exercises



class ExamScore:
    """Used to store the score of a WIMS Exam as received from ADM/RAW."""
    
    
    def __init__(self, sheet, user, score, attempts):
        self.sheet = sheet
        self.user = user
        self.score = score
        self.attempts = attempts
