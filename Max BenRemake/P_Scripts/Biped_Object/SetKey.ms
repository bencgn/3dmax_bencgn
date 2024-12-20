
        for obj in selection do
        (
            if classOf (GetTMController obj) == BipSlave_Control do
            (
                biped.setKey obj true true true
            )

            if classOf (GetTMController obj) == Vertical_Horizontal_Turn do
            (
                biped.setKey obj true true true
            )
        )

        max set key keys
	