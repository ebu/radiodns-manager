#!/usr/bin/env python
# -*- coding: utf-8 -*-

import plugit
import actions

if __name__ == "__main__":
    plugit.load_actions(actions)
    plugit.app.run(host="0.0.0.0", debug=plugit.params.DEBUG, threaded=True)
