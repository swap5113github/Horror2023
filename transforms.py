def transforming_function(self, a, b):
    # return self.transforming_function_for_2D(a, b)
    return self.transforming_function_for_perspective(a, b)

def transforming_function_for_2D(self, a, b):
    return int(a), int(b)

def transforming_function_for_perspective(self, a, b):
    lin_b = b * self.point_y_in_perspective_view / self.height
    if lin_b > self.point_y_in_perspective_view:
        lin_b = self.point_y_in_perspective_view

    diff_a = a-self.point_x_in_perspective_view
    diff_b = self.point_y_in_perspective_view-lin_b
    factor_b = diff_b/self.point_y_in_perspective_view  # 1 when diff_b == self.point_y_in_perspective_view / 0 when diff_y = 0
    factor_b = (factor_b)**3    ######

    tr_a = self.point_x_in_perspective_view + diff_a*factor_b
    tr_b = self.point_y_in_perspective_view - factor_b*self.point_y_in_perspective_view

    return int(tr_a), int(tr_b)