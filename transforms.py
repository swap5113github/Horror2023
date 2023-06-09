def transforming_function(self, a, b):
    # return self.transforming_function_for_2D(a, b)
    return self.transforming_function_for_perspective(a, b)

def transforming_function_for_2D(self, a, b):
    return int(a), int(b)

def transforming_function_for_perspective(self, a, b):
    lin_b = b * self.vanishing_point_y / self.height
    if lin_b > self.vanishing_point_y:
        lin_b = self.vanishing_point_y

    diff_a = a-self.vanishing_point_x
    diff_b = self.vanishing_point_y-lin_b
    factor_b = diff_b/self.vanishing_point_y  # 1 when diff_b == self.vanishing_point_y / 0 when diff_y = 0
    factor_b = (factor_b)**3    ######

    tr_a = self.vanishing_point_x + diff_a*factor_b
    tr_b = self.vanishing_point_y - factor_b*self.vanishing_point_y

    return int(tr_a), int(tr_b)