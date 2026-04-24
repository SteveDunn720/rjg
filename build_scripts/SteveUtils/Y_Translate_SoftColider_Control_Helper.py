import maya.cmds as mc

def soft_colide(Upper_driver:str=None, Lower_driver:str=None, parent:str=None, push=.5,):



    ctrl_list = [Lower_driver, Upper_driver]

    out_matrix = []

    # shared logic to check how close our two drivers are 

    pma_calc = mc.createNode('plusMinusAverage', name=f'{Upper_driver}_{Lower_driver}_PMA')
    mc.setAttr(f'{pma_calc}.operation', 2)

    condition = mc.createNode('condition', name=f'{Upper_driver}_{Lower_driver}_COND')
    mc.setAttr(f'{condition}.operation', 2)
    mc.setAttr(f'{condition}.colorIfFalseR', 0)
    mc.connectAttr(f'{pma_calc}.output1D', f'{condition}.colorIfTrueR')
    mc.connectAttr(f'{pma_calc}.output1D', f'{condition}.firstTerm')

    for ctrl in ctrl_list:
        #matix calc
        mult_matrix = mc.createNode('multMatrix', name=f'{ctrl}_MM')
        dec_matrix = mc.createNode('decomposeMatrix',  name=f'{ctrl}_DM')

        mc.connectAttr(f'{ctrl}.worldMatrix[0]', f'{mult_matrix}.matrixIn[0]')
        mc.connectAttr(f'{parent}.worldInverseMatrix[0]', f'{mult_matrix}.matrixIn[1]')
        mc.connectAttr(f'{mult_matrix}.matrixSum', f'{dec_matrix}.inputMatrix')

        if ctrl == ctrl_list[0]:
            mc.connectAttr(f'{dec_matrix}.outputTranslateY', f'{pma_calc}.input1D[0]')
        else:
            mc.connectAttr(f'{dec_matrix}.outputTranslateY', f'{pma_calc}.input1D[1]')

        out_matrix.append(dec_matrix)

        # push logic

        push_mult = mc.createNode('multiplyDivide', name = f'{ctrl}_MD')
        mc.setAttr(f'{push_mult}.input2X', .5 if ctrl == ctrl_list[0] else -.5)
        mc.connectAttr(f'{condition}.outColorR', f'{push_mult}.input1X')

        pma_drive = mc.createNode('plusMinusAverage', name=f'{ctrl}_PMA')
        mc.setAttr(f'{pma_drive}.operation', 2)
        axis = 'X' if ctrl == ctrl_list[0] else 'Y'
        mc.connectAttr(f'{dec_matrix}.outputTranslateY', f'{pma_drive}.input1D[0]')
        mc.connectAttr(f'{push_mult}.outputX', f'{pma_drive}.input1D[1]')








    



    
        
    

    