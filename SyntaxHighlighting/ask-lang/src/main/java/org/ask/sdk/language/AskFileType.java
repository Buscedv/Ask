// Copyright 2000-2020 JetBrains s.r.o. and other contributors. Use of this source code is governed by the Apache 2.0 license that can be found in the LICENSE file.

package org.ask.sdk.language;

import com.intellij.openapi.fileTypes.LanguageFileType;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;

import javax.swing.*;

public class AskFileType extends LanguageFileType {

    public static final AskFileType INSTANCE = new AskFileType();

    private AskFileType() {
        super(AskLanguage.INSTANCE);
    }

    @NotNull
    @Override
    public String getName() {
        return "Ask File";
    }

    @NotNull
    @Override
    public String getDescription() {
        return "Ask file";
    }

    @NotNull
    @Override
    public String getDefaultExtension() {
        return "ask";
    }

    @Nullable
    @Override
    public Icon getIcon() {
        return AskIcons.FILE;
    }

}