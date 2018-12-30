#! python3
"""
Helper class file to calculate Taxes on Salary
"""
class TaxRule:
    def __init__(self, exemption, round_down_to_nearest_10):
        self.exemption = exemption
        self.sections = []
        self.round_down_to_nearest_10 = round_down_to_nearest_10

        # function name : add_section
        # purpose : to detrmain which section is the salary will be in and add the number of sections for this salary.
    def add_section(self, index,from_, to, tax_percent, tax_discount):
        section = self.TaxSection(index,from_,to, tax_percent, tax_discount)
        self.sections.append(section)


        # function name : _get_section_by_index
        # purpose : to get the amount inside that section which we passed by index
    def _get_section_by_index(self,index):
        for section in self.sections:
            if section.index == index:
                return section

        # function name : _calculate_annual_tax
        # purpose : get the tax for each section and add them together to return the total annual tax.
    def _calculate_annual_tax(self, annual_salary):
        remaining_salary = annual_salary - self.exemption       #get the taxable salary
        total_tax = 0
        for i in range(1,len(self.sections)+1):
            if remaining_salary == 0:
                break
            section = self._get_section_by_index(i)
            if remaining_salary > section.range:
                amount = section.range
                discount = 0
            else:
                amount = remaining_salary
                discount = section.tax_discount/100
            remaining_salary -= amount
            tax = section.calculate_tax(amount)
            total_tax += tax
            total_tax = total_tax - (total_tax * discount)
        return total_tax

        # function name : calculate_monthly_tax
        # purpose : calculate the monthly tax from the _calculate_annual_tax function
    def calculate_monthly_tax(self, monthly_salary):
        annual_salary = monthly_salary * 12
        if self.round_down_to_nearest_10:
            annual_salary = annual_salary//10*10
        annual_tax = self._calculate_annual_tax(annual_salary)
        monthly_tax = annual_tax/12
        return monthly_tax

        # function name : TaxSection
        # purpose : helper class to help calculate the tax amount for each tax section
    class TaxSection:
        def __init__(self, index, from_, to, tax_percent, tax_discount):
            self.index = index
            self.from_ = from_
            self.to = to
            self.range = self.to - self.from_
            self.tax_percent = tax_percent
            self.tax_discount = tax_discount

        def calculate_tax(self, amount):
            if amount < self.range:
                tax = amount * (self.tax_percent/100)
            else:
                tax = self.range * (self.tax_percent/100)
            return tax

# use this method to check the result of all above functions.
def test(annual_salary):
    """
    >>> test(60000)
    5823.5
    >>> test(14200)
    0.0
    >>> test(37000)
    456.0
    >>> test(52000)
    2718.0
    >>> test(82000)
    10003.5
    >>> test(207000)
    33753.5
    >>> test(307000)
    58030.0
    """
    t = TaxRule(7000, False)
    t.add_section(1,0,7200,0,0)
    t.add_section(2,7200,30000,10,80)
    t.add_section(3,30000,45000,15,40)
    t.add_section(4,45000,200000,20,5)
    t.add_section(5,200000,1000000000,22.5,0)
    print(t.calculate_monthly_tax(annual_salary/12)*12)

if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)
