// Copyright 2000-2020 JetBrains s.r.o. and other contributors. Use of this source code is governed by the Apache 2.0 license that can be found in the LICENSE file.

package org.ask.sdk.language.psi;

import com.intellij.psi.tree.IElementType;
import org.ask.sdk.language.AskLanguage;
import org.jetbrains.annotations.NonNls;
import org.jetbrains.annotations.NotNull;

public class AskElementType extends IElementType {

    public AskElementType(@NotNull @NonNls String debugName) {
        super(debugName, AskLanguage.INSTANCE);
    }

}
